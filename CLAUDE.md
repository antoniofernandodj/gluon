# Gluon — Context for Claude

This file gives you the full picture of Gluon so you can contribute without
reading every source file first. Update it when the architecture changes.

---

## What this project is

**Gluon** is a React-inspired Python UI framework that runs entirely in the
browser via WebAssembly. The execution environment is **Pyodide** (CPython 3.12
compiled to WASM) loaded by **PyScript** from a CDN. No build step — Python
source files are served by any static HTTP server and fetched by PyScript at
runtime.

The framework lives in `gluon/`. Users write `app.py`, import from `gluon`, and
PyScript runs it in the browser.

---

## Runtime environment

- Python runs inside **Pyodide** (WASM), not on the server.
- `from js import document, window, setTimeout` — exposes browser globals as
  `JsProxy` objects.
- `from pyodide.ffi import create_proxy` — wraps Python callables into JS-callable
  event handlers. **Proxies must be `.destroy()`ed** to avoid memory leaks.
- Neither `js` nor `pyodide` exist on the developer's machine; `stubs/` provides
  type stubs so editors don't report errors.
- Entry point: `index.html` → `<script type="py" src="./app.py">`.
- `pyscript.toml` maps local paths → virtual FS paths that Pyodide can import.

### JS/Python boundary rules

Python primitives (str, int, float, bool, None) auto-convert when crossing the
boundary. Everything else — JS arrays, objects — arrives as a **JsProxy**.

- `str(jsproxy)` works for JS strings but is redundant (they arrive as Python str).
- To convert a JS object/array to a Python dict/list: `.to_py()` on the JsProxy.
- To pass a Python dict as a JS object: `from pyodide.ffi import to_js; to_js(d)`.
- Awaiting a JS Promise via `await jsproxy` is supported — Pyodide makes Promises
  awaitable in Python coroutines.

---

## Architecture: how a render works

```
@component fn  →  VNode tree  →  create_dom()  →  real DOM elements
                                       ↑
                              fiber context (_current_fiber)
                              enables hooks inside the fn call
```

### VNode (`gluon/core/vdom.py`)

Plain Python dataclass (`type`, `props`, `children`, `key`).

- `type` is a string tag (`'div'`) for DOM nodes, or the component function for
  component nodes.
- Element functions (`div`, `button`, …) are closures from `_el(tag)` that return
  VNodes. Props come from `**kwargs`; children from `*args`.

### Fiber (`gluon/core/fiber.py`)

One `Fiber` per component *type* (Phase 1 limitation; per-instance in Phase 2).
Stores `hooks: list` and `hook_index: int`. The global `_current_fiber` is set
right before calling a component function and restored in `finally`. This is how
hooks know which state slot they own.

### Hooks (`gluon/core/hooks.py`)

`use_state(initial)` reads `_current_fiber`, advances `hook_index`, appends to
`hooks` on first render, and returns `(value, setter)`. The setter writes to the
fiber's slot and calls `schedule_rerender()`. Functional-update form
(`set_value(lambda old: old + 1)`) is supported.

### Scheduler (`gluon/core/scheduler.py`)

`schedule_rerender()` posts a single `setTimeout(0)` (via a long-lived
`create_proxy`) if none is already pending. Multiple `set_state` calls from the
same event are batched into one render pass. On flush, calls
`renderer._root_rerender()` (import deferred to avoid circular import).

### Renderer (`gluon/core/renderer.py`)

- `render(component_wrapper, container)` — mounts the root. Unwraps `@component`
  via `._component_fn`, creates/retrieves the root fiber, calls `_do_render()`.
- `_do_render()` — saves focus (DOM path selector), destroys old proxies, calls
  the root fn, calls `create_dom()`, replaces `container.innerHTML`, restores focus.
- `create_dom(vnode, proxies)` — recursive. Handles `None/False` (skip),
  strings/ints (text nodes), `FragmentNode` (DocumentFragment), lists
  (DocumentFragment), component VNodes (`_expand_component`), element VNodes.
- `_expand_component(vnode, proxies)` — retrieves or creates the fiber for the
  component function, sets `_current_fiber`, calls `_call_fn`, recurses into
  `create_dom` with the result.
- `_call_fn(fn, props, children)` — matches declared parameters against `props`
  and `children`. Supports `*args`, `**kwargs`, `*args + **kwargs`, keyword-only
  params, and positional params filled from children in order.
- `_apply_props(el, props, proxies)` — maps prop names (`class_` → `class`),
  attaches event listeners via `create_proxy`, sets inline styles from dicts.
- `_focus_selector(container, active)` — builds a `:nth-of-type` CSS selector to
  restore focus after re-render.

### Component decorator (`gluon/core/component.py`)

`@component` wraps the original function. When called inside a render tree, the
wrapper returns a VNode (doesn't call the function yet). The original is stored at
`._component_fn` for fiber lookup. Class-based `Component` uses a metaclass so
`MyClass(prop=x)` inside a tree returns a VNode rather than an instance.

### HTTP client (`gluon/http.py`)

Thin wrapper around the browser's native `window.fetch`. All methods are async.

- `get(url, **kwargs)`, `post(url, **kwargs)`, `put`, `patch`, `delete`, `head` —
  convenience functions that call `request(url, method=..., **kwargs)`.
- `request(url, method, headers, body, json, mode, credentials, cache, signal)` —
  builds the `fetch` init dict and returns `HttpResponse`.
- `HttpResponse` wraps the JS `Response`: `.ok`, `.status`, `.status_text`.
  Body methods: `await resp.text()`, `await resp.json()`, `await resp.blob()`,
  `await resp.array_buffer()`.
- **`resp.json()` uses `json.loads(await resp.text())`** — this is intentional.
  The JS `Response.json()` method returns a JS Promise that resolves to a JS
  object (JsProxy), not a Python dict. Using `json.loads` guarantees native Python
  dicts that component code can call `.get()`, `.items()`, etc. on.
- The `init` dict is passed as a Python dict to `_js_fetch`. Pyodide passes it as
  a PyProxy; `fetch` reads properties from it. This works for all standard options.

---

## File map

```
gluon/
  __init__.py       Public re-exports only. No logic.
  http.py           HTTP client: HttpResponse, request, get/post/put/patch/delete/head
  core/
    vdom.py         VNode, FragmentNode, fragment(), _el(), all HTML element fns
    fiber.py        Fiber, _current_fiber (global mutable)
    hooks.py        use_state (Phase 3 adds use_effect, use_ref, etc.)
    component.py    @component, Component, ComponentMeta
    renderer.py     create_dom, render, _do_render, _expand_component, _call_fn
    scheduler.py    schedule_rerender, _flush, _flush_proxy

stubs/
  js.pyi            DOM type stubs (Document, Element, events, Window, …)
  pyodide/
    __init__.pyi    eval_code, JsException
    ffi.pyi         create_proxy, to_js, JsProxy, destroy_proxies
    http.pyi        pyfetch, FetchResponse

docs/               User-facing documentation (Markdown)
index.html          HTML shell. Polyfills crypto.randomUUID before loading PyScript.
pyscript.toml       [files] section mounts gluon/** into Pyodide's virtual FS.
pyrightconfig.json  stubPath = "stubs", typeCheckingMode = "basic"
app.py              Demo app. Also serves as an integration test.
examples/           Standalone runnable examples
  http_client.py    HTTP fetch demo using gluon.http
```

---

## Conventions

### Props

- Python reserved words use a trailing underscore: `class_`, `for_`, `map_`, `object_`.
- React-style aliases also accepted: `className`, `htmlFor`.
- Event handlers use camelCase React names (`onClick`, `onInput`) or lowercase HTML
  names (`onclick`, `oninput`). Both are mapped in `_EVENT_MAP` in `renderer.py`.
- `style` is a dict with camelCase or kebab-case keys.
- Boolean props: `True` → `setAttribute(attr, '')`, `False` → omit the attribute.

### Component calling conventions (inside `_call_fn`)

1. `fn(*args, **kwargs)` — call `fn(*children, **props)`.
2. `fn(**kwargs)` only — inject `children` into props dict.
3. `fn(*args)` only — call `fn(*children, **keyword_only_props)`.
4. Named positional params — fill from `props` first, then from `children` in order.

### Async components and event handlers

Event handlers can be `async def`. PyScript / Pyodide schedules them as
coroutines. State setters called before an `await` execute synchronously; those
called after resume on the event loop. Always use the functional-update form
(`set_value(lambda old: ...)`) when updating state after an `await` to avoid
stale-closure bugs.

### Proxy lifecycle

All `create_proxy` calls happen in `_apply_props`. Proxies travel through the
recursive `create_dom` call in a local `proxies` list. After render, `_do_render`
replaces `_active_proxies` with the new list and destroys every proxy from the
previous render. Never hold proxies across renders without explicit lifetime
management.

---

## Current limitations (Phase 1)

| Limitation | Root cause | Fix in |
|---|---|---|
| Full tree replacement per render | `innerHTML = ''` in `_do_render` | Phase 2 |
| One fiber per component **type** | `_fiber_registry` keyed by fn | Phase 2 |
| No `use_effect` | Not implemented | Phase 3 |
| No context API | Not implemented | Phase 3 |
| No router | Not implemented | Phase 4 |
| No global store | Not implemented | Phase 5 |

---

## Planned phases

- **Phase 2** — VDOM diffing and reconciliation. Patch only changed DOM nodes.
  Per-instance fibers keyed by position in the component tree.
- **Phase 3** — `use_effect(fn, deps)` with cleanup and async support, `use_ref`,
  `use_memo`, `use_reducer`, `create_context` / `use_context`.
- **Phase 4** — Client-side router. `HashRouter`, `Route`, `Link`, `use_navigate`,
  `use_params`, `use_location`.
- **Phase 5** — Global store. `create_store(initial, actions)` (Zustand-style),
  `use_store(store, selector)`.
- **Phase 6** — Error boundaries, lazy/async components, portals,
  CSS-in-Python helpers.

---

## Things to watch out for

- **Stale closures** — same issue as React. After `await`, local variables from
  before the await are stale. Use `set_value(lambda old: old + 1)` not
  `set_value(value + 1)` inside async handlers.
- **`inspect.signature`** is called in `_call_fn` on every render. It's slightly
  slow in Pyodide; Phase 2 may cache it per component type.
- **`input` shadows `builtins.input`** in files that do `from gluon import input`.
- **Browser cache** — PyScript fetches Python files via HTTP. During development,
  a hard refresh (`Ctrl+Shift+R`) is needed after editing framework files, because
  the browser caches them aggressively. Using `Cache-Control: no-store` on the dev
  server avoids this.
- **`resp.json()` must use `json.loads`** — never replace it with
  `await self._js_response.json()`. The JS method returns a JsProxy of a JS object,
  which doesn't have Python dict methods like `.get()`. See `gluon/http.py`.
- **`setTimeout` proxy** in the scheduler is created lazily to avoid calling
  `create_proxy` before Pyodide's JS bridge is initialised.
