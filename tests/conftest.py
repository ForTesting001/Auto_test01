import os
import pytest
import string
import logging
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import sys
import asyncio

# FORCE SELECTOR EVENT LOOP FOR WINDOWS 7 COMPATIBILITY
if sys.platform == 'win32':
    # Clear any pre-existing loop policies to avoid conflicts
    asyncio.set_event_loop_policy(None)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, "data", "config.env")
load_dotenv(dotenv_path=ENV_PATH)

os.environ["NODE_SKIP_PLATFORM_CHECK"] = "1"

SCREENSHOT_DIR = os.path.join(BASE_DIR, "data", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

LOG_FILE = os.path.join(BASE_DIR, "data", "automation.log")
worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")

if worker_id == "master" or worker_id == "gw0":
    if os.path.exists(LOG_FILE):
        try:
            os.remove(LOG_FILE)
        except Exception:
            pass

logging.basicConfig(
    level=logging.INFO,
    format=f"%(asctime)s [%(levelname)s] ({worker_id}-%(process)d) - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AutomationFramework")

def get_screenshot_path(nodeid: str) -> str:
    """Generates an absolute file path inside the data/screenshots directory."""
    valid_chars = f"-_.{string.ascii_letters}{string.digits}"
    safe_name = "".join(c if c in valid_chars else "_" for c in nodeid)
    return os.path.join(SCREENSHOT_DIR, f"{safe_name}.png")

@pytest.fixture(scope="function")
async def browser_context():
    """Pure function-scoped browser context runner with dynamic headless configuration."""
    chrome_path = os.getenv("CHROME_EXECUTABLE_PATH")
    if not chrome_path or not os.path.exists(chrome_path):
        logger.error(f"[FATAL] Chrome binary path invalid: {chrome_path}")
        pytest.fail(f"[FATAL] Chrome binary path invalid: {chrome_path}")
        
    # NEW UPDATE: Read environmental configuration and map string token to native boolean
    env_headless = os.getenv("HEADLESS_MODE", "True").strip().lower()
    is_headless = env_headless in ("true", "1", "yes")
        
    logger.info(f"[FIXTURE] Launching automated Chrome instance (Headless Mode = {is_headless}) via worker...")
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            executable_path=chrome_path,
            headless=is_headless, # FIX: Dynamic headless execution injected here
            slow_mo=200 if not is_headless else 0 # Optimization: Remove slow_mo injection when running headless to maximize speed
        )
        context = await browser.new_context()
        yield context
        
        await context.close()
        await browser.close()
        logger.info("[FIXTURE] Browser session destroyed successfully.")

# ==============================================================================
# NEW UPDATE (Lesson 14): Centralized API Request Context Fixture
# ==============================================================================
@pytest.fixture(scope="function")
async def api_client():
    """
    Provides a centralized, isolated Playwright APIRequestContext for HTTP testing.
    Automatically handles session disposal after test execution completes.
    """
    logger.info("[FIXTURE] Bootstrapping centralized API Request Context...")
    async with async_playwright() as playwright:
        # Create an isolated network context pointed at our local backend server
        api_request_context = await playwright.request.new_context(
            base_url="http://127.0.0.1:8000"
        )
        
        # Hand over the configured client to the test case
        yield api_request_context
        
        # Clean teardown: Release network resources immediately after test finishes
        await api_request_context.dispose()
        logger.info("[FIXTURE] API Request Context successfully disposed.")