# State

State is data that belongs to a component and, when changed, triggers a
re-render. Gluon's state API is the `use_state` hook, modelled after React's
`useState`.

---

## `use_state`

```python
value, set_value = use_state(initial)
```

- `initial` — the value for the first render. Can be any Python object.
- `value` — the current value for this render.
- `set_value` — a function that updates the state and schedules a re-render.

```python
from gluon import component, use_state
from gluon import div, button, p

@component
def Counter():
    count, set_count = use_state(0)

    return div(
        p(f"Count: {count}"),
        button("-", onClick=lambda e: set_count(count - 1)),
        button("+", onClick=lambda e: set_count(count + 1)),
    )
```

---

## Rules of hooks

- Call `use_state` at the **top level** of a component function — never inside
  an `if`, `for`, or nested function.
- Call it only inside a `@component` function, never in helpers or event handlers.

These rules exist because Gluon identifies each state slot by its call order
within the component. If the order changes between renders, slots get mixed up.

```python
# WRONG — conditional hook call
@component
def Broken(show_extra):
    value, set_value = use_state(0)
    if show_extra:
        extra, set_extra = use_state("")   # order changes depending on show_extra
    ...

# CORRECT — both hooks always called
@component
def Fixed(show_extra):
    value, set_value = use_state(0)
    extra, set_extra = use_state("")
    ...
```

---

## Factory initialiser

Pass a zero-argument callable to avoid creating the initial object on every
render call (it's only called once, on mount):

```python
todos, set_todos = use_state(list)        # same as use_state([])
data,  set_data  = use_state(dict)        # same as use_state({})
items, set_items = use_state(lambda: ["Buy milk", "Walk the dog"])
```

---

## Updating state

### Replace with a new value

```python
set_name("Alice")
set_items([1, 2, 3])
set_active(True)
```

### Derive from the previous value

Pass a function that receives the current state and returns the next state.
This form is safe to use inside closures and async handlers:

```python
set_count(lambda n: n + 1)
set_todos(lambda lst: [*lst, "New item"])
set_items(lambda lst: [x for x in lst if x != removed])
```

### Skipping re-renders

The setter uses identity comparison (`is not`) before scheduling a re-render.
Replacing a value with the **same object** (same `id()`) does not trigger a
re-render. Always produce new objects:

```python
# This will NOT trigger a re-render (same list object):
todos.append("New")
set_todos(todos)

# This WILL trigger a re-render (new list):
set_todos([*todos, "New"])
```

---

## Multiple state variables

Each `use_state` call is independent:

```python
@component
def Form():
    name,  set_name  = use_state("")
    email, set_email = use_state("")
    valid, set_valid = use_state(False)

    def on_name(e):
        v = e.target.value
        set_name(v)
        set_valid(bool(v and email))

    def on_email(e):
        v = e.target.value
        set_email(v)
        set_valid(bool(name and v))

    return form(
        input(type="text",  value=name,  onInput=on_name,  placeholder="Name"),
        input(type="email", value=email, onInput=on_email, placeholder="Email"),
        button("Submit", type="submit", disabled=not valid),
    )
```

---

## State and batching

Multiple `set_*` calls within the same synchronous event handler are batched
into a single re-render:

```python
def reset(e):
    set_name("")      # ← no render yet
    set_email("")     # ← no render yet
    set_valid(False)  # ← no render yet
    # one re-render fires on the next event-loop tick
```

---

## State with async handlers

State setters work inside `async def` handlers, but be careful about stale
closures. Variables captured before an `await` are frozen at their pre-await
values. Use the functional-update form to read the _current_ state:

```python
@component
def SearchBox():
    query,   set_query   = use_state("")
    results, set_results = use_state([])
    loading, set_loading = use_state(False)

    async def search(e):
        q = e.target.value
        set_query(q)
        set_loading(True)
        try:
            resp = await get(f"https://api.example.com/search?q={q}")
            if resp.ok:
                data = await resp.json()
                # Use functional form — 'results' from the closure is stale
                set_results(lambda _: data["items"])
        finally:
            set_loading(False)

    return div(
        input(type="search", value=query, onInput=search),
        p("Searching…") if loading else None,
        ul(*[li(r["title"]) for r in results]) if results else None,
    )
```

Key rule: if you call `set_value` **after** an `await`, the value captured in
the closure before the `await` may be outdated. Always use
`set_value(lambda old: ...)` when you need the current state after an await.

---

## Derived values

Compute derived values directly in the render function — no special hook needed:

```python
@component
def Cart():
    items, set_items = use_state([])

    total    = sum(item["price"] * item["qty"] for item in items)
    is_empty = len(items) == 0

    return div(
        p("Your cart is empty.") if is_empty else ul(
            *[li(f'{item["name"]} × {item["qty"]}') for item in items]
        ),
        p(f"Total: ${total:.2f}"),
    )
```

---

## Lifting state up

When two components need to share state, move it to their common parent and pass
it down as props:

```python
@component
def Parent():
    value, set_value = use_state("")

    return div(
        InputField(value=value, on_change=set_value),
        Preview(value=value),
    )

@component
def InputField(value="", on_change=None):
    return input(
        type="text",
        value=value,
        onInput=lambda e: on_change and on_change(e.target.value),
    )

@component
def Preview(value=""):
    return p(f"Preview: {value}")
```
