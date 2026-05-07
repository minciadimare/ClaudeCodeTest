from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

router = APIRouter(tags=["pages"])


@router.get("/", response_class=HTMLResponse)
async def home():
    """Serve the user upload page."""
    templates_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
    with open(os.path.join(templates_dir, "index.html"), "r") as f:
        return f.read()


@router.get("/admin/label", response_class=HTMLResponse)
async def admin_label():
    """Serve the admin labeling interface."""
    templates_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
    try:
        with open(os.path.join(templates_dir, "admin", "label.html"), "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Admin labeling interface coming soon</h1>"


@router.get("/admin/stats", response_class=HTMLResponse)
async def admin_stats():
    """Serve the admin statistics page."""
    templates_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
    try:
        with open(os.path.join(templates_dir, "admin", "stats.html"), "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Admin statistics page coming soon</h1>"
