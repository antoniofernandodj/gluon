# """
# Example: fetching data from an API using gluon.http.

# Demonstrates:
#   - `get()` convenience function
#   - async/await with the browser's native fetch API
#   - rendering API responses in a component tree
# """

# from __future__ import annotations

# from gluon import component, use_state, render, div, h1, h2, p, button, ul, li, span
# from gluon.http import get, HttpResponse
# from js import document


# @component
# def UserList():
#     users: list[dict[str, str]]
#     set_users = use_state([])

#     loading: bool
#     set_loading = use_state(False)

#     error: str
#     set_error = use_state("")

#     async def fetch_users(e):
#         set_loading(True)
#         set_error("")
#         try:
#             resp: HttpResponse = await get(
#                 "https://jsonplaceholder.typicode.com/users?_limit=5"
#             )
#             if resp.ok:
#                 data = await resp.json()
#                 set_users(data)
#             else:
#                 set_error(f"Request failed: {resp.status} {resp.status_text}")
#         except Exception as exc:
#             set_error(str(exc))
#         finally:
#             set_loading(False)

#     return div(
#         h2("Users from JSONPlaceholder API"),
#         button(
#             "Fetch Users",
#             onClick=fetch_users,
#             style={
#                 "padding": "6px 14px",
#                 "background": "#0077ff",
#                 "color": "white",
#                 "border": "none",
#                 "border-radius": "4px",
#                 "cursor": "pointer",
#                 "marginBottom": "12px",
#             },
#         ),
#         p("Loading…", style={"color": "#888"}) if loading else None,
#         p(error, style={"color": "#e74c3c"}) if error else None,
#         ul(
#             *[
#                 li(
#                     span(user.get("name", "Unknown"), style={"fontWeight": "bold"}),
#                     p(user.get("email", ""), style={"color": "#555", "marginTop": "2px"}),
#                     style={
#                         "padding": "8px 0",
#                         "borderBottom": "1px solid #eee",
#                     },
#                 )
#                 for user in users
#             ],
#             style={"listStyle": "none", "padding": "0", "margin": "0"},
#         ) if users else None,
#         style={
#             "border": "1px solid #ddd",
#             "borderRadius": "8px",
#             "padding": "16px",
#             "margin": "12px 0",
#             "background": "#fafafa",
#             "fontFamily": "system-ui, sans-serif",
#         },
#     )


# @component
# def App():
#     return div(
#         h1("🌐 HTTP Client Demo"),
#         p(
#             "All network calls use the browser's native fetch API (JS), not Python urllib.",
#             style={"color": "#555", "marginTop": "0"},
#         ),
#         UserList(),
#         style={
#             "fontFamily": "system-ui, sans-serif",
#             "maxWidth": "600px",
#             "margin": "32px auto",
#             "padding": "0 16px",
#         },
#     )


# render(App, document.getElementById("root"))
