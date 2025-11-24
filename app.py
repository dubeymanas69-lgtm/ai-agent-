from flask import Flask, request, jsonify, send_file
import os
import sys
import json

# ROBUST PATH HANDLING
# Get the absolute path of the directory containing this file (project/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (root of the repo)
root_dir = os.path.dirname(current_dir)

# Add root_dir to sys.path if not present
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Now we can import from project...
from project.agents.ai_agent import process_user_message
from project.agents.task_manager import get_all_tasks, add_task, delete_task, update_task

app = Flask(__name__)

# In-memory history
CHAT_HISTORY = []

@app.route('/')
def home():
    try:
        # Serve dashboard.html from project/web_ui/dashboard.html
        dashboard_path = os.path.join(current_dir, 'web_ui', 'dashboard.html')
        return send_file(dashboard_path)
    except FileNotFoundError:
        return "Error: project/web_ui/dashboard.html not found.", 404

@app.route('/api/tasks', methods=['GET', 'POST'])
def handle_tasks():
    if request.method == 'GET':
        tasks = get_all_tasks()
        return jsonify(tasks)
    
    if request.method == 'POST':
        data = request.json
        if isinstance(data, list):
            current_ids = {t['id'] for t in get_all_tasks()}
            for t in data:
                if t['id'] in current_ids:
                    update_task(t['id'], {
                        'task_name': t['task_name'],
                        'duration_minutes': t.get('duration_minutes'),
                        'priority': t.get('priority'),
                        'deadline': t.get('deadline'),
                        'scheduled_date': t.get('scheduled_date')
                    })
                else:
                    add_task(
                        task_name=t['task_name'],
                        duration_minutes=t.get('duration_minutes'),
                        priority=t.get('priority'),
                        deadline=t.get('deadline'),
                        scheduled_date=t.get('scheduled_date')
                    )
            return jsonify({"status": "synced"})
        else:
            return jsonify({"status": "ok"})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    CHAT_HISTORY.append({'role': 'user', 'text': user_message})
    
    parsed = process_user_message(user_message, CHAT_HISTORY)
    
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
    elif action == "update_task":
        if params.get("task_id"):
            update_task(params.get("task_id"), params.get("updates", {}))
    
    response_text = parsed.get("response", "Done.")
    CHAT_HISTORY.append({'role': 'assistant', 'text': response_text})
    
    return jsonify({
        "response": response_text,
        "action": action
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
