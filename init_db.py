import sqlite3

def init_db():
    conn = sqlite3.connect('comments.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        comment TEXT
    )
    ''')
    c.execute("INSERT INTO comments (comment) VALUES ('Test comment')")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()

