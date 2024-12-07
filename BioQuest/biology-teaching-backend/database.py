import sqlite3

def init_db():
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY,
            topic TEXT,
            question TEXT,
            correct_answer TEXT
        )
    ''')
    conn.commit()
    # 添加示例题目
    cursor.execute("INSERT INTO questions (topic, question, correct_answer) VALUES (?, ?, ?)",
                   ("biology", "What is the powerhouse of the cell?", "Mitochondria"))
    conn.commit()
    conn.close()

init_db()
print("Database initialized!")
