from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

class Entry(BaseModel):
    user_id: int
    start_time: datetime | None = None
    end_time: datetime | None = None

DB_URL = os.getenv("DATABASE_URL")

def get_db():
    conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
    return conn

@app.post("/start")
def start_time(entry: Entry):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO time_entries (user_id, start_time) VALUES (%s, %s)", 
                (entry.user_id, entry.start_time or datetime.now()))
    conn.commit()
    cur.close()
    conn.close()
    return  {"status":"started"}

@app.post("/stop")
def stop_time(entry: Entry):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
                UPDATE time_entries 
                SET end_time = %s 
                WHERE user_id = %s AND end_time IS NULL
                RETURNING id
                """, (entry.end_time or datetime.utcnow(), entry.user_id))
    if cur.rowcount == 0:
        raise HTTPException(status_code=400, detail="No active entry found for this user")
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "stopped"}

@app.get("/summary/{user_id}")
def summary (user_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM v_time_summary WHERE user_id = %s ORDER BY day DESC", (user_id,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result