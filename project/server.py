import http.server
import socketserver
import json
import os
import sys
from urllib.parse import urlparse

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project.agents.ai_agent import process_user_message
from project.agents.task_manager import get_all_tasks, add_task, delete_task, update_task
from project.main import handle_command

PORT = 8000

# Simple in-memory history
CHAT_HISTORY = []

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            try:
                with open('project/web_ui/dashboard.html', 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.wfile.write(b"Error: project/web_ui/dashboard.html not found.")
            return

        if parsed_path.path == '/api/tasks':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            tasks = get_all_tasks()
            self.wfile.write(json.dumps(tasks).encode('utf-8'))
            return
            
        super().do_GET()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_message = data.get('message', '')
            
            # Update history
            CHAT_HISTORY.append({'role': 'user', 'text': user_message})
            
            # Process
            parsed = process_user_message(user_message, CHAT_HISTORY)
            
            # Execute Action
            action = parsed.get("action")
            params = parsed.get("parameters", {})
            
            if action == "add_task":
                add_task(
                    task_name=params.get("task_name"),
                    duration_minutes=params.get("duration_minutes"),
                    priority=params.get("priority"),
                    deadline=params.get("deadline"),
                    scheduled_date=params.get("scheduled_date")
                )
            elif action == "delete_task":
                # This is tricky via chat unless we have ID. 
                # For now, we rely on the UI for deletion, or AI needs to be smarter.
                pass 
            elif action == "update_task":
                if params.get("task_id"):
                    update_task(params.get("task_id"), params.get("updates", {}))

            response_text = parsed.get("response", "Done.")
            CHAT_HISTORY.append({'role': 'assistant', 'text': response_text})
            
            response = {
                "response": response_text,
                "action": action
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
            
        if parsed_path.path == '/api/tasks':
            # Bulk update/save from UI (e.g. Drag and Drop updates)
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            tasks_data = json.loads(post_data.decode('utf-8'))
            
            # If it's a list, it's a bulk save (or we treat it as such)
            # But our task_manager uses SQL. We should probably expose an endpoint for updating a single task 
            # or handle the list intelligently.
            # For simplicity, if the UI sends the whole list, we might need to upsert.
            # BUT, for Drag and Drop, we usually just update ONE task's date.
            
            # Let's change the UI to send specific updates, OR handle the list.
            # Handling the list:
            for t in tasks_data:
                # Upsert
                existing = get_all_tasks() # Inefficient but safe
                ids = [x['id'] for x in existing]
                
                if t['id'] in ids:
                    update_task(t['id'], {
                        'task_name': t['task_name'],
                        'duration_minutes': t['duration_minutes'],
                        'priority': t['priority'],
                        'deadline': t['deadline'],
                        'scheduled_date': t.get('scheduled_date')
                    })
                else:
                    add_task(
                        task_name=t['task_name'],
                        duration_minutes=t['duration_minutes'],
                        priority=t['priority'],
                        deadline=t['deadline'],
                        scheduled_date=t.get('scheduled_date')
                    )
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
            return

        self.send_error(404)

def run():
    current_dir = os.path.dirname(os.path.abspath(__file__)) 
    root_dir = os.path.dirname(current_dir) 
    os.chdir(root_dir)
    
    socketserver.TCPServer.allow_reuse_address = True
    print(f"Starting backend server on port {PORT}...")
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    run()
