import json
import os
from pathlib import Path

# Assuming running from project root, data dir is relative
DATA_DIR = Path("data")
TASKS_FILE = DATA_DIR / "tasks.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_tasks():
    if not TASKS_FILE.exists():
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
