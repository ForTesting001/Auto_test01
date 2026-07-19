import os
import pytest
import logging
import pytest_html
from pages.login_page import LoginPage
from conftest import get_screenshot_path

# Bind to the centralized logger initialized inside conftest.py
logger = logging.getLogger("AutomationFramework")

@pytest.mark.parametrize(
    "test_name, username, password, expected_keyword",
    [
        ("Wrong password scenario", "admin", "wrong_pass", "ERROR:"),
        ("Non-existent user scenario", "intruder_user", "any_password", "ERROR:"),
        ("Empty credentials scenario", " ", " ", "ERROR:"),
        ("SQL Injection attempt scenario", "admin'--", "123456", "ERROR:"),
        ("Valid admin credentials scenario", "admin", "admin123", "SUCCESS:")
    ]
)
async def test_enterprise_login_portal(browser_context, request, extra, test_name, username, password, expected_keyword):
    """
    Asynchronous test execution integrated with standard DevOps logging handlers.
    """
    # UPDATE: Replaced print statement with explicit level-based logging execution
    logger.info(f"--- STARTING TEST CASE: {test_name} ---")
    target_url = os.getenv("TARGET_URL")
    
    if not target_url:
        logger.error("[FATAL] TARGET_URL environment variable is missing inside config.env!")
        pytest.fail("[FATAL] TARGET_URL environment variable is not defined!")

    page = await browser_context.new_page()
    login_page = LoginPage(page)
    
    logger.info(f"Navigating automated context browser tab to: {target_url}")
    await login_page.navigate_to(target_url)
    
    logger.info(f"Injecting payload data grid into login components. User: '{username}'")
    await login_page.execute_login(username, password)
    
    alert_text = await login_page.get_alert_text()
    logger.info(f"Server response captured on client screen: '{alert_text}'")
    
    full_photo_path = get_screenshot_path(request.node.nodeid)
    try:
        await page.screenshot(path=full_photo_path, full_page=False)
        filename = os.path.basename(full_photo_path)
        relative_report_path = f"screenshots/{filename}"
        extra.append(pytest_html.extras.image(relative_report_path))
        logger.info(f"Screenshot successfully committed to disk architecture: {relative_report_path}")
    except Exception as e:
        logger.warning(f"Failed to capture frame state screenshot: {e}")
        
    try:
        assert expected_keyword in alert_text, f"Assertion failed during: {test_name}"
        logger.info(f"=== TEST CASE PASSED: {test_name} ===")
    except AssertionError as ae:
        logger.error(f"=== TEST CASE FAILED: {test_name} === | Detail: {ae}")
        raise ae
    finally:
        await page.close()