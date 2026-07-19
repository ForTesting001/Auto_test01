import pytest
import logging
import requests

logger = logging.getLogger("AutomationFramework")

def test_hybrid_token_injection_bypass():
    """
    HYBRID TEST CASE: Lightweight HTTP Session architecture optimized for Windows 7.
    Bypasses Playwright subprocess limitations via safe standard HTTP network pipelines.
    """
    logger.info("--- STARTING HYBRID AUTOMATION TEST CASE (WINDOWS 7 OPTIMIZED) ---")
    
    base_url = "http://127.0.0.1:8000"
    login_payload = {"username": "admin", "password": "admin123"}
    
    session = requests.Session()
    
    # Step 1: Dispatch rapid background API login request
    logger.info("[HYBRID] Step 1: Dispatching rapid API login request...")
    api_response = session.post(f"{base_url}/api/v1/auth/login", json=login_payload)
    
    assert api_response.status_code == 200, f"Expected 200 OK, got {api_response.status_code}"
    api_data = api_response.json()
    jwt_token = api_data["token"]
    logger.info(f"[HYBRID] Step 1 Success: Extracted authorization token -> {jwt_token}")
    
    # Step 2: Inject token into HTTP Session headers exclusively
    logger.info("[HYBRID] Step 2: Injecting token into HTTP Session headers...")
    session.headers.update({
        "Authorization": f"Bearer {jwt_token}"
    })
    
    # Step 3: Route straight to the protected dashboard landing page
    logger.info("[HYBRID] Step 3: Routing straight to /dashboard via injected session...")
    dashboard_response = session.get(f"{base_url}/dashboard")
    
    # Step 4: Validate HTTP response state
    logger.info("[HYBRID] Step 4: Validating structural state of the returned dashboard HTML...")
    
    assert dashboard_response.status_code == 200, f"Security Wall Blocked! Got status {dashboard_response.status_code}"
    
    html_content = dashboard_response.text
    logger.info(f"log info html_content: {html_content}")

    # logger.info(f"[DB_TEST] Raw DB Records retrieved: {records}")
    
    # Assertions phase to confirm security bypass success
    assert "Enterprise Operation Dashboard" in html_content
   
    logger.info("=== HYBRID AUTOMATION TEST CASE PASSED ===")