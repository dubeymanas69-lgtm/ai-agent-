from project.utils.file_utils import load_json
from datetime import datetime

DATA_FILE = 'project/data/tasks.json'

def generate_summary():
    """
    Generates a text summary of tasks:
    - Total tasks
    - Tasks by priority
    - Upcoming deadlines
    """
    tasks = load_json(DATA_FILE)
    
    if not tasks:
        return "No tasks found."
        
    total_tasks = len(tasks)
    priority_counts = {"high": 0, "medium": 0, "low": 0}
    
    for task in tasks:
        p = task.get('priority', 'low').lower()
        if p in priority_counts:
            priority_counts[p] += 1
            
    # Sort by deadline for upcoming
    def sort_key(task):
        try:
            return datetime.strptime(task['deadline'], "%Y-%m-%d")
        except ValueError:
            return datetime.max
            
    sorted_tasks = sorted(tasks, key=sort_key)
    upcoming = sorted_tasks[:3]
    
    summary = []
    summary.append("=== Task Summary ===")
    summary.append(f"Total Tasks: {total_tasks}")
    summary.append("By Priority:")
    for p, count in priority_counts.items():
        summary.append(f"  - {p.capitalize()}: {count}")
        
    summary.append("Upcoming Deadlines:")
    for t in upcoming:
        summary.append(f"  - {t['name']} (Due: {t['deadline']})")
        
    return "\n".join(summary)
