# ![Gluon](icon.png)

A React-inspired Python UI framework that runs entirely in the browser via WebAssembly, powered by [PyScript](https://pyscript.net) and [Pyodide](https://pyodide.org).

Write component-based UIs in pure Python — no JavaScript required.

```python
from gluon import component, use_state, render
from gluon import div, h1, button, p
from js import document

@component
def Counter():
    count, set_count = use_state(0)
    return div(
        h1('Hello from Gluon'),
        p(f'Count: {count}'),
        button('-', onClick=lambda e: set_count(count - 1)),
        button('+', onClick=lambda e: set_count(count + 1)),
    )

render(Counter, document.getElementById('root'))
```

---

## Getting started

No build step, no package manager, no installation. You only need a static file server.

**1. Clone or copy this repository.**

**2. Start a local server from the project root:**

```bash
python -m http.server 8000
# or
npx serve .
```

**3. Open `http://localhost:8000` in your browser.**

> Always use `localhost` (not `0.0.0.0` or a LAN IP). Some browser security APIs — including ones PyScript depends on — are restricted to secure contexts, and `localhost` qualifies as one.

The first load takes a few seconds while PyScript downloads the Pyodide WASM runtime (~10 MB). Subsequent loads are cached by the browser.

---

## How it works

```tree
index.html
  └─ loads PyScript (CDN script tag)
        └─ PyScript fetches gluon/*.py from the live server
              └─ Pyodide (Python 3.12 in WASM) runs app.py
                    └─ Gluon renders components to the real DOM via js/pyodide FFI
```

PyScript exposes the browser's JavaScript globals through the `js` module and provides `pyodide.ffi.create_proxy` to turn Python callables into JS-callable event handlers.

---

## Components

### Functional components (preferred)

Decorate any Python function with `@component`. It receives props as keyword arguments and returns a VNode tree built with element functions.

```python
@component
def Greeting(name='World'):
    return h1(f'Hello, {name}!')

# Use inside another component:
@component
def App():
    return div(
        Greeting(name='Gluon'),
    )
```

**Children** — positional arguments become children. Named parameters that aren't found in the props dict are filled from positional children in declaration order:

```python
@component
def Badge(text, color='#0077ff'):
    return span(text, style={'background': color, 'color': 'white'})

# Called as:
Badge('New', color='#e74c3c')
```

For components that forward arbitrary children:

```python
@component
def Card(*children, class_=None):
    return div(*children, class_=class_)

@component
def Panel(children=None, title=''):
    return div(h2(title), *children)

@component
def Box(**props):                     # accepts everything
    children = props.pop('children', [])
    return div(*children, **props)
```

### Class-based components (fallback)

Use when you prefer grouping related logic in a class. Subclass `Component` and implement `render()`.

```python
from gluon import Component

class Clock(Component):
    def __init__(self, timezone='UTC'):
        self.timezone = timezone

    def render(self):
        return p(f'Timezone: {self.timezone}')
```

---

## HTTP client — `gluon.http`

Gluon ships a built-in HTTP client backed by the browser's native `fetch` API.
All functions are `async` — use them inside `async def` event handlers.

```python
from gluon import component, use_state, div, button, ul, li, p
from gluon.http import get

@component
def UserList():
    users,   set_users   = use_state([])
    loading, set_loading = use_state(False)
    error,   set_error   = use_state("")

    async def fetch_users(e):
        set_loading(True)
        set_error("")
        try:
            resp = await get("https://jsonplaceholder.typicode.com/users?_limit=5")
            if resp.ok:
                set_users(await resp.json())
            else:
                set_error(f"{resp.status} {resp.status_text}")
        except Exception as exc:
            set_error(str(exc))
        finally:
            set_loading(False)

    return div(
        button("Fetch Users", onClick=fetch_users),
        p("Loading…") if loading else None,
        p(error, style={"color": "red"}) if error else None,
        ul(*[li(user["name"]) for user in users]) if users else None,
    )
```

### Functions

| Function | Description |
| -------- | ----------- |
| `await get(url, **kw)` | GET request |
| `await post(url, json=..., **kw)` | POST with JSON body |
| `await put(url, **kw)` | PUT request |
| `await patch(url, **kw)` | PATCH request |
| `await delete(url, **kw)` | DELETE request |
| `await head(url, **kw)` | HEAD request |
| `await request(url, method, ...)` | Full control |

### `HttpResponse`

| Member | Type | Description |
| ------ | ---- | ----------- |
| `.ok` | `bool` | `True` if status 200–299 |
| `.status` | `int` | HTTP status code |
| `.status_text` | `str` | Status message |
| `await .json()` | `Any` | Parse body as JSON → Python `dict` / `list` |
| `await .text()` | `str` | Raw body as a string |
| `await .blob()` | `JsProxy` | JS Blob (images, files) |
| `await .array_buffer()` | `JsProxy` | JS ArrayBuffer (binary data) |

### Sending JSON

```python
resp = await post(
    "https://api.example.com/items",
    json={"name": "widget", "qty": 3},
)
```

`Content-Type: application/json` is set automatically when `json=` is used.

### Custom headers

```python
resp = await get(
    "https://api.example.com/protected",
    headers={"Authorization": "Bearer my-token"},
)
```

> All requests go through `window.fetch` and are subject to the same CORS rules
> as regular browser requests. JSONPlaceholder and most public APIs have CORS
> enabled; your own API must as well (or use a proxy).

---

## State — `use_state`

```python
value, set_value = use_state(initial)
```

- `initial` can be any value or a zero-argument factory callable (`use_state(list)`)
- `set_value(new_value)` — replace state
- `set_value(lambda old: old + 1)` — derive from previous value (safe for closures)
- Calling `set_value` schedules a re-render on the next event-loop tick; multiple calls within the same event are batched into one render

```python
@component
def Form():
    name, set_name   = use_state('')
    email, set_email = use_state('')

    def submit(e):
        e.preventDefault()
        # … handle submission

    return form(
        input(type='text',  value=name,  onInput=lambda e: set_name(e.target.value)),
        input(type='email', value=email, onInput=lambda e: set_email(e.target.value)),
        button('Submit', type='submit'),
        onSubmit=submit,
    )
```

---

## Element functions

Every standard HTML element is a callable that returns a virtual DOM node:

```python
div(*children, **props)
```

```python
# Structural
div, p, section, article, aside, header, footer, main, nav
ul, ol, li, dl, dt, dd
table, thead, tbody, tfoot, tr, th, td
form, fieldset, legend, details, summary, dialog
figure, figcaption, blockquote, pre, address

# Headings
h1, h2, h3, h4, h5, h6

# Inline
span, a, strong, em, b, i, u, s, code, kbd, mark
small, sub, sup, label, abbr, cite, q, time

# Form / interactive
button, select, option, optgroup, textarea, input
output, progress, meter

# Media
img, video, audio, source, track, canvas, iframe, svg

# Misc
hr, br, link, meta, style, noscript, template, slot, menu

# Grouping without a wrapper element
fragment
```

> `input` shadows Python's built-in `input()`. If you need both in the same file, import the built-in first: `import builtins; py_input = builtins.input`.

---

## Props

Props are passed as keyword arguments.

### Class

```python
div('hello', class_='card')          # Python-safe alias
div('hello', className='card')       # React-style alias
```

### Style

Pass a dict with camelCase or kebab-case keys:

```python
div('hello', style={'fontSize': '1.2rem', 'background-color': '#eee'})
```

### Events

Use camelCase React-style names or lowercase HTML names:

```python
button('Click', onClick=handler)
input(onInput=lambda e: set_val(e.target.value))
form(onSubmit=lambda e: (e.preventDefault(), handle()))
```

| Prop | DOM event |
| ---- | --------- |
| `onClick` / `onclick` | `click` |
| `onChange` / `onchange` | `change` |
| `onInput` / `oninput` | `input` |
| `onSubmit` / `onsubmit` | `submit` |
| `onKeyDown` / `onKeyUp` | `keydown` / `keyup` |
| `onFocus` / `onBlur` | `focus` / `blur` |
| `onMouseEnter` / `onMouseLeave` | `mouseenter` / `mouseleave` |
| `onScroll` | `scroll` |
| … | … |

### Boolean attributes

```python
input(type='checkbox', checked=True, disabled=False)
```

### Special aliases

| Prop | HTML attribute |
| ---- | -------------- |
| `class_` / `className` | `class` |
| `for_` / `htmlFor` | `for` |
| `tabIndex` | `tabindex` |
| `readOnly` | `readonly` |
| `autoFocus` | `autofocus` |
| `colSpan` / `rowSpan` | `colspan` / `rowspan` |

### Raw HTML

```python
div(dangerouslySetInnerHTML={'__html': '<strong>raw</strong>'})
```

---

## Fragments

Render multiple siblings without a wrapper element:

```python
from gluon import fragment

@component
def Items():
    return fragment(
        li('First'),
        li('Second'),
    )
```

---

## Mounting the app

```python
from js import document
from gluon import render

render(App, document.getElementById('root'))
```

`render` accepts either a `@component`-decorated function or a `Component` subclass.

---

## Project layout

```tree
gluon/              Framework source (loaded by PyScript via pyscript.toml)
├── __init__.py     Public API
├── http.py         HTTP client (get, post, put, patch, delete, head, HttpResponse)
└── core/
    ├── vdom.py     VNode + all HTML element functions
    ├── fiber.py    Per-component state container (hooks storage)
    ├── hooks.py    use_state (more hooks coming in Phase 3)
    ├── component.py  @component decorator + Component base class
    ├── renderer.py   VDOM → real DOM, event proxy management
    └── scheduler.py  Batched re-render via setTimeout(0)

stubs/              Type stubs for js and pyodide (editor support)
├── js.pyi
└── pyodide/
    ├── __init__.pyi
    ├── ffi.pyi
    └── http.pyi

docs/               User-facing guides
├── getting-started.md
├── components.md
├── state.md
├── http.md
└── elements.md

examples/           Standalone runnable demos
└── http_client.py  Fetch API demo

app.py              Demo application
index.html          HTML entry point
pyscript.toml       PyScript config (declares which files to mount)
pyrightconfig.json  Pyright / Pylance configuration
```

---

## Roadmap

| Phase | Status | Feature |
| ----- | ------ | ------- |
| 1 | ✅ Done | `@component`, `use_state`, full element library, event handling, HTTP client |
| 2 | Planned | VDOM diffing & reconciliation (no more full-tree replacement) |
| 3 | Planned | `use_effect`, `use_ref`, `use_memo`, `use_reducer`, `use_context` / `create_context` |
| 4 | Planned | Client-side router — `HashRouter`, `Route`, `Link`, `use_navigate`, `use_params` |
| 5 | Planned | Global store — `create_store`, `use_store` (Zustand-style) |
| 6 | Planned | Error boundaries, lazy/async components, portals |

---

## Known limitations (Phase 1)

- **Full re-render on every state update.** The entire component tree is rebuilt on each change. Focus is preserved automatically via DOM-path tracking, but animations and complex form state may flicker. Phase 2 introduces reconciliation.
- **One fiber per component type.** Two instances of the same component share state. Proper per-instance fibers arrive in Phase 2.
- **No `use_effect`** yet — side effects must be triggered manually from event handlers.
- **First load is slow** (~5–15 s) due to Pyodide WASM bootstrap. Subsequent loads use the browser cache.

---

## Browser support

Any browser with WebAssembly support (all modern browsers). Requires a secure context (`https://` or `localhost`) for certain Web APIs.
