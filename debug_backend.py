import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from project.agents.task_manager import add_task, get_all_tasks
from project.agents.ai_agent import process_user_message
from project.main import handle_command

def test_db():
    print("Testing DB Insertion...")
    try:
        t = add_task("Test Task DB", 30, "2025-12-31", "high")
        print(f"Success: Added task {t['id']}")
        
        tasks = get_all_tasks()
        found = any(x['id'] == t['id'] for x in tasks)
        print(f"Task found in DB: {found}")
    except Exception as e:
        print(f"DB Error: {e}")

def test_llm():
    print("\nTesting LLM Processing...")
    msg = "Add a task to buy milk tomorrow for 15 minutes priority low"
    try:
        parsed = process_user_message(msg)
        print(f"Parsed JSON: {parsed}")
        
        if parsed.get("action") == "add_task":
            response = handle_command(parsed)
            print(f"Handle Command Response: {response}")
        else:
            print("Failed to parse as add_task")
            
    except Exception as e:
        print(f"LLM Error: {e}")

if __name__ == "__main__":
    test_db()
    # Check if API keys are set before testing LLM
    if os.environ.get("LLM_API_KEY"):
        test_llm()
    else:
        print("\nSkipping LLM test (no API key set in this shell)")
