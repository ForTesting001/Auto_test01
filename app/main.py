import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# 1. Initialize the main FastAPI Application instance
app = FastAPI(
    title="Enterprise QA Target System", 
    description="Local system simulation for automation testing project."
)

# 2. Configure Jinja2 to locate our frontend HTML files safely across different OS
templates = Jinja2Templates(directory=os.path.join("app", "templates"))

# 3. Secure Centralized Mock Database containing valid credentials
MOCK_DATABASE = {
    "admin": "admin123",
    "sysops": "devops2026"
}

# ==============================================================================
# WEB FRONTEND ROUTE (GET): Serves the clean UI login portal
# ==============================================================================
@app.get("/", response_class=HTMLResponse)
def get_login_interface(request: Request):
    """Renders the login page template with an empty status."""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "status_message": "", "status_type": ""}
    )

# ==============================================================================
# WEB FRONTEND ROUTE (POST): Processes form submissions from the browser
# ==============================================================================
@app.post("/", response_class=HTMLResponse)
def handle_form_login(
    request: Request, 
    username: str = Form(...), 
    password: str = Form(...)
):
    """Validates submitted form fields against the Mock Database."""
    # Check if user exists and password matches
    if username in MOCK_DATABASE and MOCK_DATABASE[username] == password:
        msg = f"SUCCESS: Welcome back Master, {username}!"
        msg_type = "success"
    else:
        msg = "ERROR: Invalid username or password."
        msg_type = "error"
        
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "status_message": msg, "status_type": msg_type}
    )