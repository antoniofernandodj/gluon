# Components

A component is a Python function decorated with `@component` that returns a
virtual DOM tree. Gluon calls it during render and turns the result into real
DOM elements.

---

## Functional components

The standard way to define a component:

```python
from gluon import component
from gluon import div, h2, p

@component
def Welcome():
    return div(
        h2("Welcome to Gluon"),
        p("A React-inspired Python UI framework."),
    )
```

Use it inside another component just like an element function:

```python
@component
def App():
    return div(
        Welcome(),
    )
```

---

## Props

Pass data to a component as keyword arguments:

```python
@component
def Greeting(name="World", color="#333"):
    return h2(f"Hello, {name}!", style={"color": color})

# Usage
Greeting(name="Alice", color="#0077ff")
```

Props with Python reserved names use a trailing underscore (`class_`, `for_`,
`type_`). Inside the component, they arrive with the underscore included.

---

## Children

Positional arguments become the component's children:

```python
@component
def Card(*children):
    return div(*children, class_="card")

# Usage
Card(
    h2("Title"),
    p("Body text"),
)
```

Named parameters that are missing from the props dict are filled from positional
children in declaration order:

```python
@component
def Badge(text, color="#0077ff"):
    return span(text, style={"background": color, "color": "white"})

# Both of these work:
Badge("New")                      # text="New", color default
Badge("Hot", color="#e74c3c")     # text="Hot", color="#e74c3c"
Badge("Sale", "#27ae60")          # text="Sale", color="#27ae60"
```

For components that forward all children and accept arbitrary props:

```python
@component
def Box(*children, **props):
    return div(*children, **props)

# Usage
Box(p("Content"), class_="box", style={"padding": "16px"})
```

To receive children as a named parameter:

```python
@component
def Panel(children=None, title=""):
    return div(
        h3(title),
        *children,
    )

Panel(p("Content"), p("More"), title="My Panel")
```

---

## Nesting components

```python
@component
def Avatar(src, size=40):
    return img(src=src, style={"width": f"{size}px", "border-radius": "50%"})

@component
def UserCard(name, avatar_url):
    return div(
        Avatar(src=avatar_url, size=48),
        span(name),
        class_="user-card",
    )

@component
def App():
    return div(
        UserCard(name="Alice", avatar_url="/alice.png"),
        UserCard(name="Bob",   avatar_url="/bob.png"),
    )
```

---

## Conditional rendering

Return `None` or `False` to render nothing:

```python
@component
def Alert(message="", type_="info"):
    if not message:
        return None      # renders nothing

    colors = {"info": "#0077ff", "error": "#e74c3c", "success": "#27ae60"}
    return div(
        message,
        style={"background": colors.get(type_, "#eee"), "padding": "8px"},
    )
```

Inline with the ternary operator:

```python
p("Loading…") if loading else None
```

---

## Lists

Use a list comprehension inside `*[...]`:

```python
@component
def TodoList(todos):
    return ul(
        *[li(todo) for todo in todos],
    )
```

Returning a plain Python list from a component also works — Gluon wraps it
in a `DocumentFragment`:

```python
@component
def Items(items):
    return [li(item) for item in items]
```

---

## Class-based components

Use when you prefer grouping related logic in a class. Subclass `Component`
and implement `render()`:

```python
from gluon import Component
from gluon import div, h3, p

class InfoPanel(Component):
    def __init__(self, title="", body=""):
        self.title = title
        self.body  = body

    def render(self):
        return div(
            h3(self.title),
            p(self.body),
        )

# Usage inside a functional component
InfoPanel(title="Note", body="Class components work too.")
```

Class-based components cannot use hooks (`use_state`, etc.). Use functional
components for anything stateful.

---

## The `@component` decorator

`@component` wraps the function so that calling it inside a render tree returns
a `VNode` (a description of the component) rather than executing it immediately.
Gluon calls the actual function later, during `create_dom`, with the fiber
(state storage) as context.

This is why hooks work: by the time the function body runs, `_current_fiber` is
set to the correct fiber for that component.

```python
# This creates a VNode — the function hasn't run yet:
node = MyComponent(title="Hello")

# Gluon calls MyComponent(title="Hello") internally during rendering.
```

---

## `fragment` — siblings without a wrapper

Render multiple sibling elements without adding a `<div>` to the DOM:

```python
from gluon import fragment

@component
def Rows():
    return fragment(
        tr(td("Alice"), td("30")),
        tr(td("Bob"),   td("25")),
    )
```

Returning a plain list from a component achieves the same result.
