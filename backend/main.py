# main.py
# A fresh, clean, and robust implementation for the TimeTracker backend.

import os
import logging
from datetime import datetime, timezone
from uuid import UUID

import psycopg2
from psycopg2.extras import RealDictCursor, register_uuid
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ====================================================================
# 1. SETUP & CONFIGURATION
# ====================================================================

# Load environment variables from a .env file
load_dotenv()

# Configure logging to see output in the console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Register the UUID adapter for psycopg2 to handle UUID types correctly
register_uuid()


# ====================================================================
# 2. APPLICATION CONSTANTS
# ====================================================================

# This is the single, fixed user ID for the entire application.
# It's loaded from the .env file.
try:
    FIXED_USER_ID = UUID(os.environ.get("FIXED_USER_ID"))
except (ValueError, TypeError):
    logger.error("FATAL: FIXED_USER_ID is not defined in your .env file or is not a valid UUID.")
    exit()

# Get the database connection URL from the .env file
DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    raise RuntimeError("FATAL: DATABASE_URL environment variable is not set in your .env file.")


# ====================================================================
# 3. PYDANTIC MODELS (Data Shapes)
# ====================================================================

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
    entry_id: UUID | None


# ====================================================================
# 4. FASTAPI APP & DATABASE DEPENDENCY
# ====================================================================

app = FastAPI(title="TimeTracker API")

# Configure CORS to allow the frontend to communicate with the backend
origins = [
    "http://localhost:5173",  # For local development
    "http://127.0.0.1:5173",
    "https://timetracker.einfachnurphu.io", 
    "https://timetracker-backend-f7hj.onrender.com/"# Your production URL
    # Add your Render URL if it's different
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    """
    FastAPI Dependency to manage database connections.
    This function will be called for every API request that needs a database connection.
    It automatically opens a connection and ensures it's closed afterward.
    """
    conn = None
    try:
        conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
        yield conn # The connection is "yielded" to the API endpoint function
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Could not connect to the database.")
    finally:
        if conn:
            conn.close() # The connection is closed here, after the request is finished.

# Type hint for the dependency
DbConnection = Depends(get_db)


# ====================================================================
# 5. API ENDPOINTS
# ====================================================================

@app.get("/api/user/me", response_model=User)
def get_current_user(conn=DbConnection):
    """Fetches the details for the fixed user."""
    logger.info(f"Fetching details for fixed user: {FIXED_USER_ID}")
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, email FROM users WHERE id = %s", (FIXED_USER_ID,))
        user = cur.fetchone()
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Fixed user not found in the database.")
        return user

@app.get("/api/entries", response_model=list[TimeEntry])
def get_user_entries(conn=DbConnection):
    """Fetches all time entries for the fixed user."""
    logger.info(f"Fetching all entries for fixed user: {FIXED_USER_ID}")
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, user_id, start_time, end_time FROM time_entries WHERE user_id = %s ORDER BY start_time DESC",
            (FIXED_USER_ID,)
        )
        entries = cur.fetchall()
        return entries

@app.post("/api/start", response_model=StatusResponse, status_code=status.HTTP_201_CREATED)
def start_time(conn=DbConnection):
    """Starts a new time tracking entry for the fixed user."""
    logger.info(f"Received start request for fixed user: {FIXED_USER_ID}")
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM time_entries WHERE user_id = %s AND end_time IS NULL", (FIXED_USER_ID,))
        if cur.fetchone():
            raise HTTPException(status.HTTP_409_CONFLICT, "An open time entry already exists for this user.")

        query = "INSERT INTO time_entries (user_id, start_time) VALUES (%s, %s) RETURNING id"
        cur.execute(query, (FIXED_USER_ID, datetime.now(timezone.utc)))
        new_entry = cur.fetchone()
        conn.commit()
        return {"status": "started", "entry_id": new_entry['id']}

@app.post("/api/stop", response_model=StatusResponse)
def stop_time(conn=DbConnection):
    """Stops the last open time tracking entry for the fixed user."""
    logger.info(f"Received stop request for fixed user: {FIXED_USER_ID}")
    with conn.cursor() as cur:
        query = """
            UPDATE time_entries SET end_time = %s
            WHERE id = (
                SELECT id FROM time_entries
                WHERE user_id = %s AND end_time IS NULL
                ORDER BY start_time DESC LIMIT 1
            )
            RETURNING id;
        """
        cur.execute(query, (datetime.now(timezone.utc), FIXED_USER_ID))
        updated_entry = cur.fetchone()
        if not updated_entry:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No open time entry was found to stop.")
        conn.commit()
        return {"status": "stopped", "entry_id": updated_entry['id']}

