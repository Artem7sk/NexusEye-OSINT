import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            requests_count INTEGER DEFAULT 0,
            is_premium BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id, username):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
    conn.commit()
    conn.close()

def update_request_count(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET requests_count = requests_count + 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
