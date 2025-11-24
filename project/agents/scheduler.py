from datetime import datetime, timedelta
from pathlib import Path
# Adjusted imports
from project.agents.prioritizer import sort_tasks
from project.agents.task_manager import get_all_tasks

WEEK_START_HOUR = 9
WEEK_END_HOUR = 18
# Using relative path from project root
OUTPUT_ICS = Path("data/schedule.ics")

def to_ical_datetime(dt):
    return dt.strftime("%Y%m%dT%H%M%S")

def schedule_week(start_date=None):
    """
    Schedules tasks for the week starting from start_date.
    If start_date is None, defaults to the next Monday.
    """
    if start_date is None:
        now = datetime.now()
        days_ahead = 0 - now.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        start_date = now + timedelta(days=days_ahead)
        # Ensure it's a date object if it was datetime
        if isinstance(start_date, datetime):
            start_date = start_date.date()

    tasks = get_all_tasks()
    tasks = sort_tasks(tasks)
    
    # build available slots: each day from start_date for 7 days, from 09:00 to 18:00
    slots = []
    for i in range(7):
        day = start_date + timedelta(days=i)
        # Create datetime from date
        slot_start = datetime.combine(day, datetime.min.time()).replace(hour=WEEK_START_HOUR)
        slot_end = slot_start.replace(hour=WEEK_END_HOUR)
        slots.append([slot_start, slot_end])
        
    events = []
    for t in tasks:
        dur = t.get("duration_minutes")
        if not dur:
            dur = 60 # Default duration
        else:
            dur = int(dur)
            
        # find first slot where this duration fits
        placed = False
        for s in slots:
            start, end = s
            available_minutes = int((end - start).total_seconds()//60)
            if available_minutes >= dur:
                ev_start = start
                ev_end = start + timedelta(minutes=dur)
                events.append({
                    "uid": t["id"],
                    "start": ev_start,
                    "end": ev_end,
                    "summary": t["task_name"]
                })
                # move slot start forward
                s[0] = ev_end
                placed = True
                break
        if not placed:
            # no slot in week; skip or add as overflow at end of week
            pass
            
    write_ics(events)
    return events

def write_ics(events):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//simple-scheduler//EN"
    ]
    for e in events:
        lines += [
            "BEGIN:VEVENT",
            f"UID:{e['uid']}",
            f"DTSTAMP:{to_ical_datetime(datetime.utcnow())}",
            f"DTSTART:{to_ical_datetime(e['start'])}",
            f"DTEND:{to_ical_datetime(e['end'])}",
            f"SUMMARY:{e['summary']}",
            "END:VEVENT"
        ]
    lines.append("END:VCALENDAR")
    
    # Ensure directory exists
    OUTPUT_ICS.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_ICS, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Schedule written to {OUTPUT_ICS}")
