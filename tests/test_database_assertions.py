import pytest
import logging
import requests
import sqlite3
import os

logger = logging.getLogger("AutomationFramework")
# Resolve absolute path relative to the test file location to guarantee sync
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "security_audit.db")

def test_backend_database_audit_logs():
    """
    DATABASE ASSERTIONS TEST CASE:
    1. Fire one invalid and one valid API authentication request.
    2. Establish a direct low-level connection to the SQLite audit database.
    3. Execute SQL queries to verify raw backend system state persistence.
    """
    logger.info("--- STARTING DATABASE AUDIT ASSERTIONS TEST CASE ---")
    base_url = "http://127.0.0.1:8000"
    
    # Trigger a FAILED login attempt
    logger.info("[DB_TEST] Step 1: Dispatching a malicious/invalid login request...")
    requests.post(f"{base_url}/api/v1/auth/login", json={"username": "hacker_user", "password": "bad"})
    
    # Trigger a SUCCESSFUL login attempt
    logger.info("[DB_TEST] Step 2: Dispatching a valid admin login request...")
    requests.post(f"{base_url}/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    
    # Connect directly to the underlying persistent storage layer
    logger.info("[DB_TEST] Step 3: Connecting to the SQLite Database file...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query the last two recorded entries inside the audit log table
    cursor.execute("SELECT username, status FROM login_audit ORDER BY id DESC LIMIT 2")
    records = cursor.fetchall()
    conn.close()
    
    logger.info(f"[DB_TEST] Raw DB Records retrieved: {records}")
    
    # Data structure validation (Notice the DESC order: last record comes first)
    # The absolute last event should be the successful admin login
    assert records[0][0] == "admin"
    assert records[0][1] == "SUCCESS"
    
    # The second to last event should be the failed intruder attempt
    assert records[1][0] == "hacker_user"
    assert records[1][1] == "FAILED"
    
    logger.info("=== DATABASE ASSERTIONS TEST CASE PASSED ===")