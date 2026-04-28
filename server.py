import os
import sys
import json
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

# Ensure current directory is in sys.path so we can import app and gluon
sys.path.insert(0, os.getcwd())

from gluon.core.ssr import render_to_static_markup, _ssr_hydration_data, get_hydration_data
from app import App

async def homepage(request):
    """
    SSR handler for the root path.
    Renders the app on the server and injects hydration data.
    """
    # 1. Load index.html template
    with open("index.html", "r") as f:
        html_content = f.read()
    
    # 2. Perform SSR
    # Clear previous hydration data to avoid accumulation
    _ssr_hydration_data.clear()
    
    try:
        # Render the App component to static HTML
        vnode_tree = App()
        ssr_html = render_to_static_markup(vnode_tree)
        
        # 3. Get collected hydration data for server components
        hydration_json = json.dumps(get_hydration_data())
        hydration_script = f'<script>window.__GLUON_HYDRATION__ = {hydration_json};</script>'
        
        # 4. Inject into the root div
        target = '<div id="root"></div>'
        replacement = f'<div id="root">{ssr_html}</div>{hydration_script}'
        final_html = html_content.replace(target, replacement)
        
        return HTMLResponse(final_html)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HTMLResponse(f"SSR Error: <pre>{e}</pre>", status_code=500)

# Define routes
routes = [
    Route("/", homepage),
    Route("/index.html", homepage),
    # Serve all files from current directory as static files
    # This includes .py, .toml, .css, etc. for PyScript
    Mount("/", app=StaticFiles(directory="."), name="static"),
]

# Create Starlette app
app = Starlette(debug=True, routes=routes)

if __name__ == "__main__":
    import uvicorn
    # Use uv run python server.py to run this
    print("🚀 Gluon Hybrid Server (Starlette) running at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
