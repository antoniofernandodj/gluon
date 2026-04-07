# Getting Started

Gluon is a React-inspired Python UI framework that runs entirely in the browser
via WebAssembly. You write components in pure Python — no JavaScript required.

---

## Prerequisites

- A modern browser (Chrome, Firefox, Safari, Edge)
- Any static file server (`python -m http.server` is enough)
- No Node.js, no pip, no build step

---

## Running the demo

```bash
git clone <repo>
cd gluon
python -m http.server 8000
```

Open `http://localhost:8000` in your browser.

> Always use `localhost`, not `0.0.0.0` or a LAN IP. Some browser security APIs
> (including ones PyScript depends on) require a secure context, and `localhost`
> qualifies as one.

The first load takes a few seconds while PyScript downloads the Pyodide WASM
runtime (~10 MB). Subsequent loads are instant — everything is cached.

---

## How it works

```
index.html
  └─ loads PyScript (CDN <script> tag)
        └─ PyScript reads pyscript.toml
              └─ fetches gluon/*.py from the server into Pyodide's virtual FS
                    └─ Pyodide (Python 3.12 in WASM) runs app.py
                          └─ Gluon renders components to the real DOM
```

The key files:

| File | Purpose |
| ---- | ------- |
| `index.html` | HTML shell — loads PyScript, defines `<div id="root">` |
| `pyscript.toml` | Tells PyScript which files to mount into Pyodide's FS |
| `app.py` | Your application code |
| `gluon/` | The framework |

---

## Your first component

Edit `app.py`:

```python
from gluon import component, use_state, render
from gluon import div, h1, p, button
from js import document

@component
def Counter():
    count, set_count = use_state(0)

    return div(
        h1("Hello from Gluon"),
        p(f"Count: {count}"),
        button("-", onClick=lambda e: set_count(count - 1)),
        button("+", onClick=lambda e: set_count(count + 1)),
    )

render(Counter, document.getElementById("root"))
```

Reload the browser. You have a working reactive counter in pure Python.

---

## How state updates work

1. A user clicks a button → the event handler calls `set_count(...)`.
2. Gluon schedules a re-render on the next event-loop tick (`setTimeout(0)`).
3. Multiple `set_*` calls in the same event are batched into one render.
4. The component function is called again with the new state values.
5. The output replaces the previous DOM.

---

## Stale browser cache

PyScript fetches Python files over HTTP and the browser caches them. After
editing any file under `gluon/`, do a **hard refresh** (`Ctrl+Shift+R` /
`Cmd+Shift+R`) to force a reload.

To disable caching during development, start the server with:

```bash
python -c "
import http.server, functools
Handler = functools.partial(
    http.server.SimpleHTTPRequestHandler,
    extensions_map={'': 'text/plain', '.py': 'text/plain'},
)
http.server.HTTPServer(('', 8000), Handler).serve_forever()
"
```

Or add `Cache-Control: no-store` via your server's configuration.

---

## Next steps

- [Components](./components.md) — `@component`, props, children, class-based
- [State](./state.md) — `use_state` patterns and async handlers
- [HTTP client](./http.md) — fetching data from APIs
- [Elements reference](./elements.md) — every HTML element and its props
