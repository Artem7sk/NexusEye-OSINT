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

def get_stats():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # Считаем общее количество юзеров и общее число запросов
    cursor.execute('SELECT COUNT(*), SUM(requests_count) FROM users')
    stats = cursor.fetchone()
    conn.close()
    return stats # Возвращает кортеж (кол-во_юзеров, кол-во_запросов)

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

def is_user_premium(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('SELECT is_premium FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else False
def set_premium_status(user_id, status: bool):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_premium = ? WHERE user_id = ?', (status, user_id))
    conn.commit()
    conn.close()

def get_detailed_stats():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # Считаем: всего юзеров, всего запросов, и сколько из них Premium
    cursor.execute('SELECT COUNT(*), SUM(requests_count), (SELECT COUNT(*) FROM users WHERE is_premium = 1) FROM users')
    stats = cursor.fetchone()
    conn.close()
    return stats # Возвращает (всего_юзеров, всего_запросов, премиум_юзеров)
