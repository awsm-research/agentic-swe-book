# task_service.py
import smtplib
import psycopg2


class TaskService:
    def __init__(self):
        self.conn = psycopg2.connect("host=localhost dbname=tasks")    # (?)

    def process(self, t, f, uid):                                      # (?)
        if t == "" or t == None:                                       # (?)
            print("bad title")
            return None
        cur = self.conn.cursor()
        cur.execute(f"INSERT INTO tasks VALUES ('{t}', '{uid}')")      # (?)
        self.conn.commit()
        smtp = smtplib.SMTP('smtp.gmail.com')                          # (?)
        smtp.sendmail('app@co.com', uid, f'Task {t} created')
        if f == True:                                                  # (?)
            cur.execute(f"SELECT * FROM tasks WHERE uid='{uid}'")
            return cur.fetchall()
        return {"title": t, "user": uid}

    def process(self, tasks, reverse):                                 # (?)
        if reverse == True:
            return sorted(tasks, key=lambda x: x['date'], reverse=True)
        else:
            return sorted(tasks, key=lambda x: x['date'])
