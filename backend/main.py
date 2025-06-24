# main.py

import os
import logging
from datetime import datetime, timezone
from uuid import UUID

import psycopg2
from psycopg2.extras import RealDictCursor, register_uuid
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# --- Konfiguration & Initialisierung ---
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
register_uuid()

# ====================================================================
# === NEU: Feste User-ID für die gesamte Anwendung ===
# Ersetzen Sie diese ID durch die ID Ihres Hauptbenutzers in der Datenbank
# ====================================================================
try:
    FIXED_USER_ID = UUID(os.environ.get("FIXED_USER_ID", 'b29ea098-08dc-4a63-bbd0-15ea5cdf9590'))
except (ValueError, TypeError):
    logger.error("FATAL: FIXED_USER_ID in .env file is not a valid UUID.")
    exit()


# --- Pydantic-Modelle ---
class User(BaseModel):
    id: UUID
    name: str | None
    email: str | None

class TimeEntry(BaseModel):
    id: UUID
    user_id: UUID
    start_time: datetime
    end_time: datetime | None

class StatusResponse(BaseModel):
    status: str
    entry_id: UUID | None = None

# --- App-Instanz und Middleware ---
app = FastAPI(title="TimeTracker API")

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Datenbankverbindung ---
DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    raise RuntimeError("FATAL: DATABASE_URL environment variable not set.")

def get_db():
    try:
        conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Could not connect to database.")


# --- API Endpunkte ---

@app.get("/api/user/me", response_model=User)
def get_current_user():
    """Gibt die Details des festen Benutzers zurück."""
    logger.info(f"Fetching details for fixed user: {FIXED_USER_ID}")
    conn = None
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email FROM users WHERE id = %s", (FIXED_USER_ID,))
            user = cur.fetchone()
            if not user:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Fixed user not found in database.")
            return user
    finally:
        if conn:
            conn.close()

@app.get("/api/entries", response_model=list[TimeEntry])
def get_user_entries():
    """Gibt eine detaillierte Liste aller Zeiteinträge für den festen Benutzer zurück."""
    logger.info(f"Fetching all entries for fixed user: {FIXED_USER_ID}")
    conn = None
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, user_id, start_time, end_time FROM time_entries WHERE user_id = %s ORDER BY start_time DESC",
                (FIXED_USER_ID,)
            )
            entries = cur.fetchall()
            return entries
    finally:
        if conn:
            conn.close()


@app.post("/api/start", response_model=StatusResponse, status_code=status.HTTP_201_CREATED)
def start_time():
    """Startet eine neue Zeitmessung für den festen Benutzer."""
    logger.info(f"Received start request for fixed user: {FIXED_USER_ID}")
    conn = None
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM time_entries WHERE user_id = %s AND end_time IS NULL", (FIXED_USER_ID,))
            if cur.fetchone():
                raise HTTPException(status.HTTP_409_CONFLICT, "An open time entry already exists.")

            query = "INSERT INTO time_entries (user_id, start_time) VALUES (%s, %s) RETURNING id"
            cur.execute(query, (FIXED_USER_ID, datetime.now(timezone.utc)))
            new_id = cur.fetchone()['id']
            conn.commit()
            return {"status": "started", "entry_id": new_id}
    finally:
        if conn:
            conn.close()


@app.post("/api/stop", response_model=StatusResponse)
def stop_time():
    """Stoppt die letzte Zeitmessung für den festen Benutzer."""
    logger.info(f"Received stop request for fixed user: {FIXED_USER_ID}")
    conn = None
    try:
        conn = get_db()
        with conn.cursor() as cur:
            query = """
                UPDATE time_entries SET end_time = %s
                WHERE id = (SELECT id FROM time_entries WHERE user_id = %s AND end_time IS NULL ORDER BY start_time DESC LIMIT 1)
                RETURNING id;
            """
            cur.execute(query, (datetime.now(timezone.utc), FIXED_USER_ID))
            updated_entry = cur.fetchone()
            if not updated_entry:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "No open time entry to stop.")
            conn.commit()
            return {"status": "stopped", "entry_id": updated_entry['id']}
    finally:
        if conn:
            conn.close()

