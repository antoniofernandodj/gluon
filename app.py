from gluon import component, server_component, use_state, render, is_browser
from gluon import div, h1, h2, p, button, hr, strong, span

# This component ONLY runs on the server during SSR.
# In the browser, it won't be re-rendered (Phase 1).
@server_component
def ServerInfo():
    import platform
    import datetime
    return div(
        h2("🖥️ Server Side Component"),
        p(f"This part was rendered on the server at {datetime.datetime.now().strftime('%H:%M:%S')}."),
        p(f"Server OS: ", strong(platform.system())),
        style={
            "border": "2px solid #ff4757",
            "padding": "15px",
            "borderRadius": "8px",
            "backgroundColor": "#fff5f5",
            "marginBottom": "20px"
        }
    )

# This is a standard hybrid component.
# It renders on the server for initial HTML, and then hydrates on the client.
@component
def InteractiveCounter():
    count, set_count = use_state(0)
    
    return div(
        h2("🖱️ Client Side Component"),
        p("This component is interactive! It hydrates in the browser."),
        div(
            button("-", onClick=lambda e: set_count(count - 1), style={"padding": "5px 15px"}),
            span(str(count), style={"fontSize": "1.5rem", "margin": "0 20px", "fontWeight": "bold"}),
            button("+", onClick=lambda e: set_count(count + 1), style={"padding": "5px 15px"}),
            style={"display": "flex", "alignItems": "center"}
        ),
        style={
            "border": "2px solid #2ed573",
            "padding": "15px",
            "borderRadius": "8px",
            "backgroundColor": "#f0fff4"
        }
    )

@component
def App():
    return div(
        h1("Gluon Hybrid Rendering"),
        p("The same code runs on the server (SSR) and the client (Hydration)."),
        hr(),
        ServerInfo(),
        InteractiveCounter(),
        style={
            "fontFamily": "system-ui, sans-serif",
            "maxWidth": "800px",
            "margin": "40px auto",
            "padding": "0 20px"
        }
    )

# Only call render if we are in the browser.
# In SSR, the server will call render_to_static_markup(App())
if is_browser():
    from js import document
    render(App, document.getElementById("root"))
