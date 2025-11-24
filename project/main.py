import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project.agents.ai_agent import process_user_message
from project.agents.task_manager import add_task, delete_task, update_task, get_all_tasks
from project.agents.prioritizer import sort_tasks
from project.agents.scheduler import schedule_week
from project.agents.ai_summary import generate_summary

def handle_command(parsed):
    action = parsed.get("action")
    params = parsed.get("parameters", {})
    
    if action == "add_task":
        t = add_task(
            task_name=params.get("task_name"),
            duration_minutes=params.get("duration_minutes"),
            deadline=params.get("deadline"),
            priority=params.get("priority", "medium"),
            earliest_start=params.get("earliest_start")
        )
        return f"Added task '{t['task_name']}' (id {t['id']})"
        
    if action == "summarize_week":
        return generate_summary()
        
    if action == "query_schedule":
        tasks = sort_tasks(get_all_tasks())
        if not tasks:
            return "No tasks found."
        lines = [f"{t['task_name']} - {t.get('deadline') or 'no deadline'} - {t.get('priority')}" for t in tasks]
        return "\n".join(lines)
        
    if action == "get_free_slots":
        # simplistic: return days with free hours
        return "Feature not implemented yet."
        
    if action == "chat":
        return params.get("response", "I couldn't understand.")
        
    return f"Action '{action}' not implemented."

def repl():
    print("AI Planner CLI. Type 'exit' to quit.")
    print("Make sure LLM_API_URL and LLM_API_KEY environment variables are set.")
    
    while True:
        try:
            msg = input("You: ").strip()
        except EOFError:
            break
            
        if msg.lower() in ("exit", "quit"):
            break
        if not msg:
            continue
            
        print("Processing...")
        parsed = process_user_message(msg)
        
        # Debug print to see what LLM returned (optional, but helpful)
        # print(f"[Debug] Parsed: {parsed}")
        
        reply = handle_command(parsed)
        print("Assistant:", reply)

if __name__ == "__main__":
    repl()
