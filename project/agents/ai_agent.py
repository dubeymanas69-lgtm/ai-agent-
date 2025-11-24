import json
import datetime
from project.llm_wrapper import call_llm

SYSTEM_PROMPT = """
You are an intelligent Task Management Assistant.
Your goal is to help the user manage their schedule and tasks.

Current Date: {current_date}

You can perform the following actions. Return ONLY a JSON object.

1. **add_task**:
   - `task_name`: string (required)
   - `duration_minutes`: integer (default 60)
   - `priority`: "high", "medium", "low" (default "medium")
   - `deadline`: "YYYY-MM-DD" (optional, for due dates)
   - `scheduled_date`: "YYYY-MM-DD" (optional, if user says "do this ON [date]")

2. **delete_task**:
   - `task_id`: string (if user provides it, otherwise ask for clarification or list tasks)
   - Note: If user says "delete the task about X", you might need to search first, but for now just ask for ID or say you can't find it. Actually, better: just return a text response asking for clarification if ID is missing.

3. **update_task**:
   - `task_id`: string
   - `updates`: object with fields to change

4. **chat**:
   - Just a normal conversation.

**Output Format**:
{
    "action": "add_task" | "delete_task" | "update_task" | "chat",
    "parameters": { ... },
    "response": "A natural language response to the user confirming the action or answering the question."
}

**Rules**:
- If the user says "Schedule X for Friday", calculate the date for the coming Friday based on Current Date and put it in `scheduled_date`.
- If the user says "Deadline is Friday", put it in `deadline`.
- `scheduled_date` is when they want to DO it. `deadline` is when it must be DONE by.
- Always be helpful and concise.
"""

def process_user_message(user_message, chat_history=[]):
    current_date = datetime.date.today().isoformat()
    
    # Format history for context
    history_text = ""
    for msg in chat_history[-5:]: # Keep last 5 messages for context
        role = msg.get('role', 'user')
        text = msg.get('text', '')
        history_text += f"{role.upper()}: {text}\n"
    
    prompt = f"""
    {SYSTEM_PROMPT.format(current_date=current_date)}

    Conversation History:
    {history_text}

    User: {user_message}
    
    JSON Response:
    """
    
    try:
        response_text = call_llm(prompt)
        # Clean up code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].strip()
            
        parsed = json.loads(response_text)
        return parsed
    except Exception as e:
        print(f"Error parsing AI response: {e}")
        return {
            "action": "chat",
            "parameters": {},
            "response": "I'm sorry, I had trouble understanding that. Could you try again?"
        }
