import json
# Adjusted imports
from project.llm_wrapper import call_llm_system
from project.agents.task_manager import get_all_tasks

SUMMARY_PROMPT = """
You are a summarizer. Input: JSON array of tasks (id, task_name, duration_minutes, deadline, priority).
Output: concise weekly summary (max 6 sentences) listing:
- total tasks
- urgent deadlines in next 7 days (list)
- estimated hours this week
- top 3 suggested tasks to focus on
Respond only with the summary text.
"""

def generate_summary():
    tasks = get_all_tasks()
    prompt = SUMMARY_PROMPT + "\n\n" + json.dumps(tasks)
    text = call_llm_system(prompt)
    return text
