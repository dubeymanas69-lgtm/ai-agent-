import uuid
from datetime import datetime
from project.utils.file_utils import load_json, save_json

DATA_FILE = 'project/data/tasks.json'

def add_task(task_name, duration_minutes, deadline_date, priority):
    """
    Adds a new task to the storage.
    
    Args:
        task_name (str): Name of the task
        duration_minutes (int): Duration in minutes
        deadline_date (str): YYYY-MM-DD
        priority (str): high, medium, or low
    """
    tasks = load_json(DATA_FILE)
    
    new_task = {
        "id": str(uuid.uuid4()),
        "name": task_name,
        "duration": int(duration_minutes),
        "deadline": deadline_date,
        "priority": priority.lower(),
        "created_at": datetime.now().isoformat()
    }
    
    tasks.append(new_task)
    save_json(DATA_FILE, tasks)
    print(f"Task '{task_name}' added successfully.")
