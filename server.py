import uvicorn
import sqlite3
import os
from datetime import datetime
from fastapi import FastAPI, status, Response, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Get the absolute directory of the current server.py file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "security_audit.db")

# Ensure the directory exists explicitly
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            username TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()

app = FastAPI(title="Enterprise Auth Mock API with DB Audit")


class LoginRequest(BaseModel):
    username: str
    password: str


def log_audit_to_db(username: str, auth_status: str):
    """Helper function to commit security logs directly into SQLite storage."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO login_audit (timestamp, username, status) VALUES (?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username, auth_status)
    )
    conn.commit()
    conn.close()


@app.post("/api/v1/auth/login")
async def mock_login(payload: LoginRequest, response: Response):
    if payload.username == "admin" and payload.password == "admin123":
        log_audit_to_db(payload.username, "SUCCESS")
        return {
            "status": "SUCCESS",
            "token": "sysops_secret_jwt_token_2026",
            "message": "Authentication token generated successfully."
        }

    log_audit_to_db(payload.username, "FAILED")
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {
        "status": "ERROR",
        "token": None,
        "message": "Invalid system credentials provided."
    }


@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    authorization = request.headers.get("authorization")
    if authorization == "Bearer sysops_secret_jwt_token_2026":
        return """<html><body><h1>Welcome to Enterprise Operation Dashboard</h1></body></html>"""

    return HTMLResponse(status_code=401, content="<html><body><h1>Access Denied</h1></body></html>")

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
