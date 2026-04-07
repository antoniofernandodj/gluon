# Gluon Documentation

Gluon is a React-inspired Python UI framework that runs entirely in the browser
via WebAssembly (Pyodide + PyScript). Write component-based UIs in pure Python —
no JavaScript required.

---

## Guides

| Guide | Description |
| ----- | ----------- |
| [Getting started](./getting-started.md) | Setup, first component, how it works |
| [Components](./components.md) | `@component`, props, children, class-based |
| [State](./state.md) | `use_state`, batching, async handlers |
| [HTTP client](./http.md) | Fetching data from APIs with `gluon.http` |
| [Elements & props](./elements.md) | Full HTML element reference and prop rules |

---

## 30-second example

```python
from gluon import component, use_state, render
from gluon import div, h1, p, button, ul, li
from gluon.http import get
from js import document

@component
def App():
    count, set_count = use_state(0)
    posts, set_posts = use_state([])

    async def load(e):
        resp = await get("https://jsonplaceholder.typicode.com/posts?_limit=3")
        if resp.ok:
            set_posts(await resp.json())

    return div(
        h1("Gluon"),
        p(f"Clicked {count} times"),
        button("Click me", onClick=lambda e: set_count(count + 1)),
        button("Load posts", onClick=load),
        ul(*[li(post["title"]) for post in posts]),
    )

render(App, document.getElementById("root"))
```

---

## Core concepts

**Components** are Python functions decorated with `@component` that return a
virtual DOM tree. Gluon calls them during render and syncs the result to the
real browser DOM.

**State** is local data managed with `use_state(initial)`. Calling the setter
schedules a re-render; multiple calls in the same event are batched into one.

**Elements** are functions (`div`, `button`, `input`, …) that return virtual
DOM nodes. Props are keyword arguments; children are positional arguments.

**HTTP** requests go through the browser's native `fetch` API via `gluon.http`.
All functions are async and return an `HttpResponse` with `.json()`, `.text()`,
and other body methods.

---

## Project structure

```
gluon/          Framework source
├── __init__.py     Public API
├── http.py         HTTP client
└── core/           Internals (vdom, fiber, hooks, renderer, scheduler)

docs/           This documentation
app.py          Demo application
index.html      HTML entry point
pyscript.toml   PyScript configuration
```
