from datetime import datetime
# Adjusted import
from project.agents.task_manager import get_all_tasks

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

def parse_date(d):
    if not d:
        return None
    try:
        return datetime.strptime(d, "%Y-%m-%d")
    except:
        return None

def sort_tasks(tasks):
    def keyfn(t):
        dd = parse_date(t.get("deadline"))
        pr = PRIORITY_RANK.get(t.get("priority", "medium").lower(), 1)
        dur = t.get("duration_minutes") or 999999
        # sort by (has_deadline_flag, deadline_date or far future, priority, duration)
        has_deadline = 0 if dd else 1
        return (has_deadline, dd or datetime(9999,1,1), pr, dur)
    return sorted(tasks, key=keyfn)
