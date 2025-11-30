import sqlite3

# create database
def init_db():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT NOT NULL,
                    keyword TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

# insert new search into db
def log_search(user_email, keyword):
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute("INSERT INTO searches (user_email, keyword) VALUES (?, ?)", (user_email, keyword))
    c.execute("""DELETE FROM searches
                 WHERE user_email=?
                 AND id NOT IN (
                     SELECT id FROM searches WHERE user_email=? ORDER BY timestamp DESC LIMIT 10
                 )""", (user_email, user_email))
    conn.commit()
    conn.close()

# get up to 10 of the user's recent searches
def get_recent_searches(user_email, limit=10):
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute("""SELECT keyword
                 FROM searches
                 WHERE user_email=?
                 ORDER BY timestamp DESC
                 LIMIT ?""", (user_email, limit))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows] # return as list of strings not tuples
