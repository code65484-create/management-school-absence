from flask import Flask, render_template, request, redirect
import sqlite3
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")
chat_model = model.start_chat(history=[])

app = Flask(__name__)

def get_db():
    db_path = os.path.join(os.path.dirname(__file__), "school.db")
    return sqlite3.connect(db_path)

def init_db():
    conn = get_db()
    cur = conn.cursor()

    classes = ["1BACSEF-1", "1BACSEG-1", "2BACSH-1"]

    for c in classes:
        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS '{c}' (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            sep INTEGER DEFAULT 0,
            oct INTEGER DEFAULT 0,
            nov INTEGER DEFAULT 0,
            dec INTEGER DEFAULT 0,
            jan INTEGER DEFAULT 0,
            feb INTEGER DEFAULT 0,
            mar INTEGER DEFAULT 0,
            apr INTEGER DEFAULT 0,
            may INTEGER DEFAULT 0,
            jun INTEGER DEFAULT 0
        )
        """)


        cur.execute(f"SELECT COUNT(*) FROM '{c}'")
        if cur.fetchone()[0] == 0:
            for i in range(1, 6):
                cur.execute(f"INSERT INTO '{c}' (name) VALUES (?)", (f"Student {i}",))

    conn.commit()
    conn.close()

@app.route('/')
def index():
    classes = ["1BACSEF-1", "1BACSEG-1", "2BACSH-1"]
    return render_template("index.html", classes=classes)

@app.route('/students/<class_name>')
def students(class_name):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT id, name FROM '{class_name}'")
    students = cur.fetchall()
    conn.close()
    return {"students": students}

@app.route('/add_absence', methods=['POST'])
def add_absence():
    class_name = request.form['class']
    student_id = request.form['student']
    month = request.form['month']
    value = request.form['value']

    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"UPDATE '{class_name}' SET {month}=? WHERE id=?", (value, student_id))
    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/report/<class_name>')
def report(class_name):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM '{class_name}'")
    data = cur.fetchall()
    conn.close()
    return render_template("report.html", data=data, class_name=class_name)


genai.configure(api_key="AIzaSyDPPAUc4UPZ9Q_4y0fOsvboY708j23JCsQ")


model = genai.GenerativeModel("gemini-2.5-flash")
chat_model = model.start_chat(history=[])


def get_db():
    db_path = os.path.join(os.path.dirname(__file__), "school.db")
    return sqlite3.connect(db_path)


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    response_text = ""

    if request.method == 'POST':
        user_message = request.form['message']

        conn = get_db()
        cur = conn.cursor()

        classes = ["1BACSEF-1", "1BACSEG-1", "2BACSH-1"]
        all_data = []

        for c in classes:
            cur.execute(f"""
            SELECT name, sep, oct, nov, dec, jan, feb, mar, apr, may, jun
            FROM '{c}'
            """)

            rows = cur.fetchall()

            for r in rows:
                total = sum(r[1:])
                all_data.append({
                    "class": c,
                    "name": r[0],
                    "total": total
                })

        conn.close()

        prompt = f"""
You are a school assistant working with a student absence management system.

The system contains multiple classes. Each class has a table of students.
Each student has absence hours recorded for every month from September to June.

Each value represents absence hours (not days).
You can calculate total absence by summing all months.

Your job:
- Analyze the data
- Calculate total absences
- Compare between students and classes
- Identify students with high absences
- Detect months with high absence
- Help the school supervisor (general supervisor) with any task related to student absences
- Give clear and direct answers

IMPORTANT:
- Always reply in the same language as the user
- If the user writes in Arabic, reply in Arabic
- If the user writes in English, reply in English
- Do not mix languages

If the data is not enough, say that clearly.

        this is data of absents:
        {all_data}

        question:
        {user_message}
        """

        try:
            response = chat_model.send_message(prompt)
            response_text = response.text
        except Exception as e:
            response_text = str(e)

    return render_template("chat.html", response=response_text)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
