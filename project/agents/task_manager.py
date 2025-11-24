import uuid
from datetime import datetime
from project.database import get_db_connection

def add_task(task_name, duration_minutes=None, deadline=None, priority="medium", scheduled_date=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    task_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    
    cursor.execute('''
        INSERT INTO tasks (id, task_name, duration_minutes, priority, deadline, created_at, scheduled_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (task_id, task_name, duration_minutes, priority, deadline, created_at, scheduled_date))
    
    conn.commit()
    conn.close()
    
    return {
        "id": task_id,
        "task_name": task_name,
        "duration_minutes": duration_minutes,
        "deadline": deadline,
        "priority": priority,
        "created_at": created_at,
        "scheduled_date": scheduled_date
    }

def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    rows_affected = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return rows_affected > 0

def update_task(task_id, updates: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Dynamic update query
    fields = []
    values = []
    for k, v in updates.items():
        fields.append(f"{k} = ?")
        values.append(v)
    
    if not fields:
        return None
        
    values.append(task_id)
    query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
    
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    
    # Return updated task (fetch it back)
    return get_task_by_id(task_id)

def get_task_by_id(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_all_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks')
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
