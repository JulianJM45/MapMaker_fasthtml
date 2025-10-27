# app.py
"""Minimal MapMaker FastHTML application - imports everything from separate files"""

from fasthtml.common import *
from modules.config import get_app_headers
from modules.routes import setup_routes
from modules.ui import get_main_page

# Create FastHTML app with headers from config
app, rt = fast_app(hdrs=get_app_headers(), pico=False)

# Setup all routes from routes module
setup_routes(rt)

# Main page route
@rt("/")
def index():
    return get_main_page()

if __name__ == "__main__":
    serve(port=5001)
