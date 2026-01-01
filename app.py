from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import date

app = Flask(__name__)

# ---------- DB ----------

def get_db():
    conn = sqlite3.connect("streakd.db")
    conn.row_factory = sqlite3.Row  # so you can use task.completed, task.streak
    return conn

def init_db_safe():
    conn = get_db()
    c = conn.cursor()

    # user table
    c.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY,
            xp INTEGER DEFAULT 0
        )
    """)
    c.execute("INSERT OR IGNORE INTO user (id, xp) VALUES (1, 0)")

    # tasks table
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            completed_date TEXT,
            streak INTEGER DEFAULT 0
        )
    """)

    # task_progress table
    c.execute("""
        CREATE TABLE IF NOT EXISTS task_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            completed_date TEXT
        )
    """)

    # Fix existing tasks table if streak column is missing
    try:
        c.execute("ALTER TABLE tasks ADD COLUMN streak INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        # Column already exists
        pass

    conn.commit()
    conn.close()

# ---------- XP & Level ----------

LEVELS = [0, 1000, 2500, 4500, 7000]

def get_level(xp):
    for i in range(len(LEVELS)):
        if xp < LEVELS[i]:
            return i
    return len(LEVELS)

def get_user_xp():
    conn = get_db()
    row = conn.execute("SELECT xp FROM user WHERE id = 1").fetchone()
    xp = row["xp"] if row else 0
    conn.close()
    return xp

# ---------- ROUTES ----------

from datetime import date

@app.route("/")
def index():
    xp = get_user_xp()
    level = get_level(xp)
    next_level_xp = LEVELS[level] if level < len(LEVELS) else LEVELS[-1]

    today = date.today().isoformat()  # YYYY-MM-DD
    conn = get_db()
    
    # Reset completed for tasks not completed today
    conn.execute("UPDATE tasks SET completed = 0 WHERE completed_date != ?", (today,))
    conn.commit()
    
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()

    # Pass 'today' to template
    return render_template("index.html", xp=xp, level=level, next_level_xp=next_level_xp, tasks=tasks, today=today)


@app.route("/add-task", methods=["POST"])
def add_task():
    task_name = request.form.get("task_name")
    if task_name:
        conn = get_db()
        conn.execute("INSERT INTO tasks (name) VALUES (?)", (task_name,))
        conn.commit()
        conn.close()
    return redirect(url_for("index"))

@app.route("/complete-task/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    conn = get_db()
    task = conn.execute("SELECT completed, streak FROM tasks WHERE id = ?", (task_id,)).fetchone()
    
    if task["completed"] == 0:
        today = date.today()
        XP_PER_TASK = 50
        conn.execute("UPDATE tasks SET completed = 1, completed_date = ?, streak = streak + 1 WHERE id = ?", (today, task_id))
        conn.execute("UPDATE user SET xp = xp + ? WHERE id = 1", (XP_PER_TASK,))
        conn.execute("INSERT INTO task_progress (task_id, completed_date) VALUES (?, ?)", (task_id, today))
        conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete-task/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# Weekly & Monthly progress (same as your previous)
@app.route("/weekly")
def weekly_progress():
    conn = get_db()
    data = conn.execute("""
        SELECT completed_date, COUNT(*) as count
        FROM task_progress
        WHERE completed_date >= date('now', '-7 days')
        GROUP BY completed_date
    """).fetchall()
    conn.close()
    return render_template("weekly.html", data=data)

@app.route("/monthly")
def monthly_progress():
    conn = get_db()
    data = conn.execute("""
        SELECT substr(completed_date, 1, 7) as month, COUNT(*) as count
        FROM task_progress
        GROUP BY month
    """).fetchall()
    
    xp_row = conn.execute("SELECT xp FROM user WHERE id = 1").fetchone()
    xp = xp_row["xp"] if xp_row else 0

    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    
    return render_template("monthly.html", data=data, xp=xp, tasks=tasks)

# ---------- RUN ----------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)






    
