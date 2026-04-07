# Elements & Props

Every standard HTML element is available as a function imported from `gluon`.
Each function accepts positional children and keyword props and returns a VNode.

```python
from gluon import div, h1, button, input, span
```

---

## Calling syntax

```python
tag(*children, **props)
```

Children can be:

- Strings or numbers → rendered as text nodes.
- Other VNodes (returned by element functions or `@component` calls).
- `None` or `False` → skipped entirely (useful for conditional rendering).
- A Python list → rendered as a sequence of siblings.

```python
div(
    h1("Title"),
    p("Paragraph"),
    None,           # skipped
    "plain text",   # text node
    [span("a"), span("b")],  # list of siblings
)
```

---

## Element reference

### Structural / block

| Function | HTML tag |
| -------- | -------- |
| `div` | `<div>` |
| `p` | `<p>` |
| `section` | `<section>` |
| `article` | `<article>` |
| `aside` | `<aside>` |
| `header` | `<header>` |
| `footer` | `<footer>` |
| `main` | `<main>` |
| `nav` | `<nav>` |

### Lists

| Function | HTML tag |
| -------- | -------- |
| `ul` | `<ul>` |
| `ol` | `<ol>` |
| `li` | `<li>` |
| `dl` | `<dl>` |
| `dt` | `<dt>` |
| `dd` | `<dd>` |

### Tables

| Function | HTML tag |
| -------- | -------- |
| `table` | `<table>` |
| `thead` | `<thead>` |
| `tbody` | `<tbody>` |
| `tfoot` | `<tfoot>` |
| `tr` | `<tr>` |
| `th` | `<th>` |
| `td` | `<td>` |

### Forms

| Function | HTML tag |
| -------- | -------- |
| `form` | `<form>` |
| `input` | `<input>` |
| `button` | `<button>` |
| `textarea` | `<textarea>` |
| `select` | `<select>` |
| `option` | `<option>` |
| `optgroup` | `<optgroup>` |
| `label` | `<label>` |
| `fieldset` | `<fieldset>` |
| `legend` | `<legend>` |
| `output` | `<output>` |
| `progress` | `<progress>` |
| `meter` | `<meter>` |

### Headings

`h1`, `h2`, `h3`, `h4`, `h5`, `h6`

### Inline

| Function | HTML tag |
| -------- | -------- |
| `span` | `<span>` |
| `a` | `<a>` |
| `strong` | `<strong>` |
| `em` | `<em>` |
| `b` | `<b>` |
| `i` | `<i>` |
| `u` | `<u>` |
| `s` | `<s>` |
| `code` | `<code>` |
| `kbd` | `<kbd>` |
| `mark` | `<mark>` |
| `small` | `<small>` |
| `sub` | `<sub>` |
| `sup` | `<sup>` |
| `abbr` | `<abbr>` |
| `cite` | `<cite>` |
| `q` | `<q>` |
| `time` | `<time>` |
| `bdi` | `<bdi>` |
| `bdo` | `<bdo>` |
| `data` | `<data>` |

### Media

| Function | HTML tag |
| -------- | -------- |
| `img` | `<img>` |
| `video` | `<video>` |
| `audio` | `<audio>` |
| `source` | `<source>` |
| `track` | `<track>` |
| `canvas` | `<canvas>` |
| `iframe` | `<iframe>` |
| `picture` | `<picture>` |
| `svg` | `<svg>` |
| `object_` | `<object>` |
| `embed` | `<embed>` |
| `map_` | `<map>` |

### Misc

| Function | HTML tag |
| -------- | -------- |
| `hr` | `<hr>` |
| `br` | `<br>` |
| `pre` | `<pre>` |
| `blockquote` | `<blockquote>` |
| `figure` | `<figure>` |
| `figcaption` | `<figcaption>` |
| `address` | `<address>` |
| `details` | `<details>` |
| `summary` | `<summary>` |
| `dialog` | `<dialog>` |
| `menu` | `<menu>` |
| `template` | `<template>` |
| `slot` | `<slot>` |
| `noscript` | `<noscript>` |
| `link` | `<link>` |
| `meta` | `<meta>` |
| `script` | `<script>` |
| `style` | `<style>` |

> `input` shadows Python's built-in `input()`. If you need both in the same file:
> ```python
> import builtins
> py_input = builtins.input
> from gluon import input   # now safe
> ```

---

## Props

### Class

```python
div("hello", class_="card")        # trailing underscore avoids Python keyword clash
div("hello", className="card")     # React-style alias also works
```

### Style

Pass a dict with camelCase or kebab-case keys:

```python
div(
    "hello",
    style={
        "fontSize": "1.2rem",       # camelCase
        "background-color": "#eee", # kebab-case — both work
        "margin": "0 auto",
    },
)
```

### Events

Use camelCase React-style names or lowercase HTML names:

```python
button("Click me", onClick=my_handler)
input(onInput=lambda e: set_val(e.target.value))
form(onSubmit=lambda e: (e.preventDefault(), handle()))
```

| Gluon prop | DOM event |
| ---------- | --------- |
| `onClick` / `onclick` | `click` |
| `onDblClick` / `ondblclick` | `dblclick` |
| `onChange` / `onchange` | `change` |
| `onInput` / `oninput` | `input` |
| `onSubmit` / `onsubmit` | `submit` |
| `onKeyDown` / `onkeydown` | `keydown` |
| `onKeyUp` / `onkeyup` | `keyup` |
| `onKeyPress` | `keypress` |
| `onFocus` / `onfocus` | `focus` |
| `onBlur` / `onblur` | `blur` |
| `onMouseEnter` | `mouseenter` |
| `onMouseLeave` | `mouseleave` |
| `onMouseMove` | `mousemove` |
| `onMouseDown` | `mousedown` |
| `onMouseUp` | `mouseup` |
| `onScroll` / `onscroll` | `scroll` |
| `onWheel` | `wheel` |
| `onContextMenu` | `contextmenu` |
| `onDragStart` | `dragstart` |
| `onDragEnd` | `dragend` |
| `onDrop` | `drop` |
| `onPointerDown` | `pointerdown` |
| `onPointerUp` | `pointerup` |
| `onPointerMove` | `pointermove` |
| `onTouchStart` | `touchstart` |
| `onTouchEnd` | `touchend` |
| `onTouchMove` | `touchmove` |

Event handlers receive the native browser `Event` object (a `JsProxy`).

```python
from js import Event

def on_click(e: Event) -> None:
    e.preventDefault()
    print(e.target.value)
```

### Boolean attributes

`True` sets the attribute with an empty string value; `False` omits it:

```python
input(type="checkbox", checked=True)
button("Submit", disabled=False)   # attribute omitted
```

### Special aliases

| Gluon prop | HTML attribute |
| ---------- | -------------- |
| `class_` / `className` | `class` |
| `for_` / `htmlFor` | `for` |
| `tabIndex` | `tabindex` |
| `readOnly` | `readonly` |
| `autoFocus` | `autofocus` |
| `autoComplete` | `autocomplete` |
| `colSpan` | `colspan` |
| `rowSpan` | `rowspan` |
| `maxLength` | `maxlength` |
| `minLength` | `minlength` |
| `crossOrigin` | `crossorigin` |
| `accessKey` | `accesskey` |

Unrecognised camelCase props (e.g. `ariaLabel`) are lowercased and set directly
as attributes.

### Raw HTML

Inject pre-rendered HTML strings (use with caution — no XSS protection):

```python
div(dangerouslySetInnerHTML={"__html": "<strong>raw content</strong>"})
```

### Data attributes

```python
div("hello", **{"data-id": "42", "data-role": "card"})
```

### ARIA attributes

```python
button("Close", **{"aria-label": "Close dialog", "aria-expanded": "false"})
```

---

## `fragment`

Render multiple siblings without a wrapper element:

```python
from gluon import fragment

fragment(
    dt("Term"),
    dd("Definition"),
)
```

Equivalent to returning a plain Python list from a component.

---

## Examples

### Controlled input

```python
@component
def NameField():
    name, set_name = use_state("")
    return div(
        label("Name:", for_="name-input"),
        input(
            id="name-input",
            type="text",
            value=name,
            onInput=lambda e: set_name(e.target.value),
            placeholder="Enter your name",
        ),
        p(f"Hello, {name}!") if name else None,
    )
```

### Select / dropdown

```python
@component
def ColorPicker():
    color, set_color = use_state("red")
    return div(
        select(
            option("Red",   value="red"),
            option("Green", value="green"),
            option("Blue",  value="blue"),
            value=color,
            onChange=lambda e: set_color(e.target.value),
        ),
        div("Preview", style={"background": color, "padding": "8px", "color": "white"}),
    )
```

### Image

```python
img(
    src="/avatar.png",
    alt="User avatar",
    style={"width": "48px", "borderRadius": "50%"},
)
```

### Anchor

```python
a("Gluon on GitHub", href="https://github.com/example/gluon", target="_blank")
```

### Form with submit

```python
@component
def LoginForm():
    email,    set_email    = use_state("")
    password, set_password = use_state("")

    def submit(e):
        e.preventDefault()
        print(f"Login: {email}")

    return form(
        input(type="email",    value=email,    onInput=lambda e: set_email(e.target.value)),
        input(type="password", value=password, onInput=lambda e: set_password(e.target.value)),
        button("Login", type="submit"),
        onSubmit=submit,
    )
```
