import sqlite3
import os
from pathlib import Path

DB_PATH = Path("project/data/tasks.db")

def get_db_connection():
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tasks table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            task_name TEXT NOT NULL,
            duration_minutes INTEGER,
            priority TEXT,
            deadline TEXT,
            created_at TEXT,
            status TEXT DEFAULT 'pending',
            scheduled_date TEXT
        )
    ''')
    
    # Check if scheduled_date column exists (migration for existing db)
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'scheduled_date' not in columns:
        print("Migrating DB: Adding scheduled_date column...")
        cursor.execute('ALTER TABLE tasks ADD COLUMN scheduled_date TEXT')
    
    conn.commit()
    conn.close()

# Initialize on module load
init_db()
