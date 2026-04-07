# Gluon — Project context for AI assistants

This file explains the architecture, conventions, and current state of Gluon so
that an AI coding assistant can understand the codebase without reading every file
first. Keep it updated when the architecture changes significantly.

---

## What this project is

**Gluon** is a React-inspired Python UI framework that runs in the browser via
WebAssembly. The execution environment is **Pyodide** (CPython 3.12 compiled to
WASM) loaded by **PyScript** from a CDN. No build step exists — the Python source
files are served by any static HTTP server and fetched by PyScript at runtime.

The framework lives entirely in the `gluon/` directory. Users write `app.py` that
imports from `gluon`, and PyScript runs it in the browser.

---

## Runtime environment

- Python runs inside **Pyodide** (WASM), not on the server.
- `from js import document, window, setTimeout` — exposes browser globals.
- `from pyodide.ffi import create_proxy` — wraps Python callables so JS can call
  them as event listeners. **Proxies must be `.destroy()`ed** to avoid memory leaks.
- Neither `js` nor `pyodide` exist on the developer's machine; `stubs/` provides
  type information so editors don't report errors.
- The entry point is `index.html` → `<script type="py" src="./app.py">`.
- `pyscript.toml` maps local file paths → virtual FS paths that Pyodide can import.

---

## Architecture: how a render works

### Data flow

```
@component fn  →  VNode tree  →  create_dom()  →  real DOM elements
                                       ↑
                              fiber context (_current_fiber)
                              enables hooks inside the fn call
```

### Key concepts

**VNode** (`gluon/core/vdom.py`)
A plain Python object (`VNode.type`, `.props`, `.children`, `.key`).
- `type` is a string tag (`'div'`) for DOM elements, or the original component
  function for component nodes.
- Element functions (`div`, `button`, `h1`, …) are closures over `_el(tag)` that
  return VNodes. Props come from `**kwargs`; children from `*args`.

**Fiber** (`gluon/core/fiber.py`)
One `Fiber` per component *type* (Phase 1 limitation; per-instance in Phase 2).
Stores `hooks: list` and `hook_index: int`. The global `_current_fiber` is set
to the active fiber right before calling a component function, and restored
immediately after (using try/finally). This is how hooks know which state slot
they own.

**Hooks** (`gluon/core/hooks.py`)
`use_state(initial)` reads `_current_fiber`, advances `hook_index`, appends to
`hooks` on first render, and returns `(value, setter)`. The setter writes to the
fiber's slot and calls `schedule_rerender()`. Functional-update form
(`set_value(lambda old: old + 1)`) is supported.

**Scheduler** (`gluon/core/scheduler.py`)
`schedule_rerender()` posts a single `setTimeout(0)` (via a long-lived
`create_proxy`) if one isn't already pending. This batches multiple `set_state`
calls from the same event into one render pass. On flush, it calls
`renderer._root_rerender()` to avoid a circular import at module level.

**Renderer** (`gluon/core/renderer.py`)
- `render(component_wrapper, container)` — mounts the root. Unwraps the
  `@component` wrapper via `._component_fn`, creates/retrieves the root fiber,
  stores both globally, calls `_do_render()`.
- `_do_render()` — saves focus (DOM path selector), destroys old proxies,
  calls the root fn with its fiber as context, calls `create_dom()`, replaces
  `container.innerHTML`, restores focus.
- `create_dom(vnode, proxies)` — recursive. Handles `None/False`, strings/ints
  (text nodes), `FragmentNode` (DocumentFragment), lists (DocumentFragment),
  component VNodes (`_expand_component`), and regular element VNodes.
- `_expand_component(vnode, proxies)` — retrieves or creates the fiber for the
  component function, sets `_current_fiber`, calls `_call_fn`, recurses into
  `create_dom` with the result.
- `_call_fn(fn, props, children)` — matches the function's declared parameters
  against `props` and `children`. Handles `*args`, `**kwargs`, `*args + **kwargs`,
  keyword-only params, and positional params filled from children in order.
- `_apply_props(el, props, proxies)` — maps prop names (`class_` → `class`),
  attaches event listeners via `create_proxy`, sets inline styles from dicts.
- `_focus_selector(container, active)` — builds a `:nth-of-type` CSS selector
  from container down to the active element so focus can be restored after re-render.

**Component decorator** (`gluon/core/component.py`)
`@component` wraps the original function. The wrapper, when called inside a
render tree, returns a VNode (doesn't call the function yet). The wrapper stores
the original function at `._component_fn` so `render()` and `_expand_component`
can look up or create the fiber. Class-based `Component` uses a metaclass so
`MyClass(prop=x)` inside a tree returns a VNode rather than an instance.

---

## File map

```
gluon/
  __init__.py       Public re-exports only. No logic.
  core/
    vdom.py         VNode, FragmentNode, fragment(), _el(), all HTML element fns
    fiber.py        Fiber, _current_fiber (global mutable)
    hooks.py        use_state (Phase 3 will add use_effect, use_ref, etc.)
    component.py    @component, Component, ComponentMeta
    renderer.py     create_dom, render, _do_render, _expand_component, _call_fn
    scheduler.py    schedule_rerender, _flush, _flush_proxy

stubs/
  js.pyi            Full DOM type stubs (Document, Element, events, Window, …)
  pyodide/
    __init__.pyi    eval_code, JsException
    ffi.pyi         create_proxy, to_js, JsProxy, destroy_proxies
    http.pyi        pyfetch, FetchResponse

index.html          HTML shell. Polyfills crypto.randomUUID before loading PyScript.
pyscript.toml       [files] section mounts gluon/** into Pyodide's virtual FS.
pyrightconfig.json  stubPath = "stubs", typeCheckingMode = "basic"
.vscode/settings.json  Same settings for Pylance.
app.py              Demo app (Counter + TodoList). Serves as integration test.
```

---

## Conventions

### Props

- Python reserved words use a trailing underscore: `class_`, `for_`, `map_`, `object_`.
- React-style aliases are also accepted: `className`, `htmlFor`.
- Event handlers use camelCase React names (`onClick`, `onInput`, …) or lowercase
  HTML names (`onclick`, `oninput`). Both are mapped in `_EVENT_MAP`.
- `style` is a dict with camelCase or kebab-case keys.
- Boolean props: `True` → `setAttribute(attr, '')`, `False` → omit.

### Component calling conventions

Components accept children as positional arguments. Inside `_call_fn`:
1. If fn has `**kwargs` + `*args` → call `fn(*children, **props)`.
2. If fn has only `**kwargs` → inject `children` into props dict.
3. If fn has only `*args` → call `fn(*children, **keyword_only_props)`.
4. Otherwise: fill declared positional params from props first, then from children
   in declaration order for any that remain unfilled.

### Proxy lifecycle

All `create_proxy` calls happen inside `create_dom` via `_apply_props`.
Proxies are appended to a local `proxies` list that travels through the recursive
call. After the render, `_do_render` replaces `_active_proxies` with the new list
and destroys every proxy from the previous render. Never hold on to proxies beyond
one render cycle without explicitly managing their lifetime.

---

## Current limitations (Phase 1)

| Limitation | Root cause | Fix in |
|------------|-----------|--------|
| Full tree replacement per render | `innerHTML = ''` in `_do_render` | Phase 2 (reconciliation) |
| One fiber per component **type** | `_fiber_registry` keyed by fn | Phase 2 (per-instance fibers) |
| No `use_effect` | Not yet implemented | Phase 3 |
| No context API | Not yet implemented | Phase 3 |
| No router | Not yet implemented | Phase 4 |
| No global store | Not yet implemented | Phase 5 |

---

## Planned phases

- **Phase 2** — VDOM diffing and reconciliation. Patch only changed DOM nodes.
  Introduce per-instance fibers keyed by component position in the tree (fiber
  tree / work-in-progress tree like React's).
- **Phase 3** — `use_effect(fn, deps)` with cleanup and async support, `use_ref`,
  `use_memo`, `use_reducer`, `create_context` / `use_context`.
- **Phase 4** — Client-side router. `HashRouter` (hash-based, zero server config),
  optional `BrowserRouter`. Components: `Route`, `Link`. Hooks: `use_navigate`,
  `use_params`, `use_location`.
- **Phase 5** — Global store. `create_store(initial, actions)` → Zustand-style.
  `use_store(store, selector)` subscribes a component to a slice of global state.
- **Phase 6** — Error boundaries, lazy/async components, portals,
  CSS-in-Python helpers.

---

## Things to watch out for

- **Stale closures** work the same as in React. `set_count(count + 1)` captures
  `count` from the current render. Use the functional form
  `set_count(lambda n: n + 1)` when updating inside async callbacks or timers.
- **`inspect.signature`** is used in `_call_fn` to introspect component parameters
  at render time. This works fine in Pyodide but is slightly slow. Phase 2 may
  cache signatures.
- **`input` shadows `builtins.input`** in any file that does
  `from gluon import input`. Document this clearly for users.
- **Proxy destruction order** matters: proxies must be destroyed *after* the new
  DOM is in place (otherwise event handlers could fire on a destroyed proxy during
  the brief overlap). The current `_do_render` destroys proxies before building the
  new tree, which is safe because the old DOM is not yet replaced when destruction
  happens.
- **`setTimeout` proxy** in the scheduler is created lazily (first call to
  `schedule_rerender`) to avoid issues when the module is imported before Pyodide's
  JS bridge is fully initialised.
