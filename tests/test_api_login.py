import pytest
import logging

logger = logging.getLogger("AutomationFramework")

@pytest.mark.asyncio
async def test_api_successful_authentication(api_client):
    """
    POSITIVE FLOW: Verifies that sending valid credentials returns HTTP 200
    and a valid session token asset.
    """
    logger.info("--- STARTING API TEST: Successful Authentication (Positive) ---")
    
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    
    # Execute HTTP POST using the centralized fixture injected directly into the function
    response = await api_client.post("/api/v1/auth/login", data=payload)
    
    logger.info(f"Response status captured: {response.status}")
    assert response.status == 200, f"Expected 200 OK, got {response.status}"
    
    response_json = await response.json()
    assert response_json["status"] == "SUCCESS"
    assert response_json["token"] == "sysops_secret_jwt_token_2026"
    
    logger.info("=== API POSITIVE TEST PASSED ===")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, description",
    [
        ("admin", "wrong_password", "Invalid password scenario"),
        ("intruder_user", "admin123", "Non-existent user scenario"),
        ("", "", "Empty payload scenario")
    ]
)
async def test_api_unauthorized_authentication(api_client, username, password, description):
    """
    NEGATIVE FLOW: Verifies that any malicious or incorrect credential combinations
    are rejected with an HTTP 401 Unauthorized code and zero active tokens.
    """
    logger.info(f"--- STARTING API TEST: {description} (Negative) ---")
    
    payload = {
        "username": username,
        "password": password
    }
    
    # Send incorrect payloads to the gatekeeper endpoint
    response = await api_client.post("/api/v1/auth/login", data=payload)
    
    logger.info(f"Response status captured for {description}: {response.status}")
    
    # CRITICAL SECURITY ASSERTION: Must return 401 Unauthorized
    assert response.status == 401, f"Security Breach! Expected 401 Unauthorized, got {response.status}"
    
    response_json = await response.json()
    assert response_json["status"] == "ERROR"
    assert response_json["token"] is None # Ensure no token leaked out
    assert "Invalid system credentials" in response_json["message"]
    
    logger.info(f"=== API NEGATIVE TEST PASSED: {description} secured ===")