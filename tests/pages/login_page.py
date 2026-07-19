# UPDATE: Switched import from sync_api to async_api
from playwright.async_api import Page

class LoginPage:
    """
    Asynchronous Page Object Model representing the Enterprise Portal Login Screen.
    All interaction methods are now non-blocking coroutines.
    """
    
    def __init__(self, page: Page):
        self.page = page
        self.username_input = "#username-input"
        self.password_input = "#password-input"
        self.submit_button = "#submit-button"
        self.alert_box = "#alert-box"

    # UPDATE: Added 'async' prefix and 'await' keywords to all communication methods
    async def navigate_to(self, url: str):
        await self.page.goto(url)

    async def fill_username(self, username: str):
        await self.page.fill(self.username_input, username)

    async def fill_password(self, password: str):
        await self.page.fill(self.password_input, password)

    async def click_submit(self):
        await self.page.click(self.submit_button)

    async def get_alert_text(self) -> str:
        # UPDATE: Resolving locator text asynchronously
        return await self.page.locator(self.alert_box).inner_text()

    async def execute_login(self, username: str, password: str):
        # UPDATE: Chaining async calls inside a unified workflow coroutine
        await self.fill_username(username)
        await self.fill_password(password)
        await self.click_submit()