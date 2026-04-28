# Gluon

A React-inspired Python UI framework that runs in the browser via WebAssembly (PyScript/Pyodide) and supports **Hybrid Rendering** (SSR + Hydration).

Write component-based UIs in pure Python — no JavaScript required.

```python
from gluon import component, server_component, use_state, render, is_browser
from gluon import div, h1, button, p, strong

@server_component
def ServerInfo():
    import platform
    return p(f"Rendered on: ", strong(platform.system()))

@component
def Counter():
    count, set_count = use_state(0)
    return div(
        h1('Hello from Gluon'),
        ServerInfo(),
        p(f'Count: {count}'),
        button('+', onClick=lambda e: set_count(count + 1)),
    )

if is_browser():
    from js import document
    render(Counter, document.getElementById('root'))
```

---

## Hybrid Rendering (SSR + Hydration)

Gluon now supports **Hybrid Rendering**. The same Python code runs on the server (to generate initial HTML for SEO and speed) and in the browser (to add interactivity).

### `@server_component`
Mark components that should only execute on the server. Their output is captured and "hydrated" as static content in the browser, preventing re-execution in the WASM environment.

### `@component`
Standard components that render on the server for the initial paint and then become fully interactive in the browser.

---

## Getting started with UV

Gluon is optimized for the [uv](https://github.com/astral-sh/uv) package manager.

**1. Clone this repository.**

**2. Install dependencies and run the hybrid server:**

```bash
uv run python server.py
```

**3. Open `http://localhost:8000` in your browser.**

The server (Starlette-based) performs **Server-Side Rendering (SSR)**. When the page loads, you see the content immediately. Once PyScript finishes loading, the interactive parts (hooks, event handlers) are hydrated.

---

## How it works

```tree
1. Browser requests /
2. server.py (Starlette) imports app.py
3. Gluon SSR renders the component tree to an HTML string
4. Initial HTML + Hydration Data is sent to the browser (Fast First Paint)
5. Browser loads PyScript (WASM)
6. app.py runs in the browser
7. Gluon Hydrator reuses the server's HTML for @server_components
8. Interactive components become live
```

---

## Components

### Functional components

Decorate any Python function with `@component`. It receives props as keyword arguments and returns a VNode tree built with element functions.

```python
@component
def Greeting(name='World'):
    return h1(f'Hello, {name}!')
```

### Server-only components

Use `@server_component` for parts of your UI that depend on server-side resources (databases, OS info, etc.) or that don't need to be interactive.

```python
@server_component
def DatabaseStatus():
    # This only runs on the server!
    status = check_db_health() 
    return p(f"DB is {status}")
```

---

## HTTP client — `gluon.http`

Gluon ships a built-in HTTP client backed by the browser's native `fetch` API.
All functions are `async` — use them inside `async def` event handlers.

```python
from gluon.http import get

@component
def UserList():
    users, set_users = use_state([])

    async def fetch_users(e):
        resp = await get("https://api.example.com/users")
        if resp.ok:
            set_users(await resp.json())

    return div(
        button("Fetch Users", onClick=fetch_users),
        ul(*[li(u["name"]) for u in users])
    )
```

---

## Roadmap

| Phase | Status | Feature |
| ----- | ------ | ------- |
| 1 | ✅ Done | `@component`, `use_state`, Hybrid Rendering (SSR), Starlette Server |
| 2 | Planned | VDOM diffing & reconciliation (no more full-tree replacement) |
| 3 | Planned | `use_effect`, `use_ref`, `use_memo`, `use_context` |
| 4 | Planned | Client-side router — `HashRouter`, `Route`, `Link` |
| 5 | Planned | Global store — `create_store`, `use_store` |

---

## Requirements

- **Python 3.12+** (uses PEP 695 generics)
- **uv** (recommended for running the server)
- **Modern Browser** with WebAssembly support

---

## Browser support

Any browser with WebAssembly support. Requires a secure context (`https://` or `localhost`) for certain Web APIs.
