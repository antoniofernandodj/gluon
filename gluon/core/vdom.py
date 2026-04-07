"""
Virtual DOM node definitions and HTML element factory functions.

Usage:
    from gluon import div, h1, button, span

    div(
        h1('Hello!'),
        button('Click', onClick=handler),
        style={'color': 'red'},
    )

Notes:
    - `input` shadows Python's builtin. Use `builtins.input` if needed.
    - Props that are Python reserved words use trailing underscore:
        class_ → class attribute
        for_   → for attribute
    - React-style aliases also work: className, htmlFor
"""

from __future__ import annotations

from typing import Any, Callable


class VNode:
    """Represents a virtual DOM node (element or component placeholder)."""
    __slots__ = ('type', 'props', 'children', 'key')

    def __init__(
        self,
        type: str | Callable[..., Any],
        props: dict[str, Any],
        children: list[Any],
        key: str | int | None = None,
    ) -> None:
        self.type: str | Callable[..., Any] = type        # str tag or callable component fn
        self.props: dict[str, Any] = props      # dict of attributes/event handlers
        self.children: list[Any] = children
        self.key: str | int | None = key

    def __repr__(self) -> str:
        t = self.type if isinstance(self.type, str) else getattr(self.type, '__name__', repr(self.type))
        return f'VNode<{t}>'


class FragmentNode:
    """Groups children without a wrapper DOM element."""
    __slots__ = ('children', 'key')

    def __init__(self, children: list[Any], key: str | int | None = None) -> None:
        self.children: list[Any] = children
        self.key: str | int | None = key


def fragment(*children: Any, key: str | int | None = None) -> FragmentNode:
    """Render multiple children without a wrapping element."""
    return FragmentNode(_flatten(children), key)


# ─── Internal helpers ──────────────────────────────────────────────────────────

def _flatten(children: tuple[Any, ...]) -> list[Any]:
    """Flatten nested lists/tuples and filter out None/False."""
    flat: list[Any] = []
    for child in children:
        if isinstance(child, (list, tuple)):
            flat.extend(_flatten(child))
        elif child is not None and child is not False:
            flat.append(child)
    return flat


def _el(tag: str) -> Callable[..., VNode]:
    """Return a VNode builder function for *tag*."""
    def builder(*children: Any, **props: Any) -> VNode:
        key = props.pop('key', None)
        return VNode(tag, props, _flatten(children), key)
    builder.__name__ = tag
    builder.__qualname__ = tag
    return builder


# ─── Block / structural ────────────────────────────────────────────────────────
div         = _el('div')
p           = _el('p')
section     = _el('section')
article     = _el('article')
aside       = _el('aside')
header      = _el('header')
footer      = _el('footer')
main        = _el('main')
nav         = _el('nav')
ul          = _el('ul')
ol          = _el('ol')
li          = _el('li')
dl          = _el('dl')
dt          = _el('dt')
dd          = _el('dd')
table       = _el('table')
thead       = _el('thead')
tbody       = _el('tbody')
tfoot       = _el('tfoot')
tr          = _el('tr')
th          = _el('th')
td          = _el('td')
form        = _el('form')
fieldset    = _el('fieldset')
legend      = _el('legend')
details     = _el('details')
summary     = _el('summary')
dialog      = _el('dialog')
figure      = _el('figure')
figcaption  = _el('figcaption')
blockquote  = _el('blockquote')
pre         = _el('pre')
address     = _el('address')

# ─── Headings ──────────────────────────────────────────────────────────────────
h1 = _el('h1')
h2 = _el('h2')
h3 = _el('h3')
h4 = _el('h4')
h5 = _el('h5')
h6 = _el('h6')

# ─── Inline ────────────────────────────────────────────────────────────────────
span        = _el('span')
a           = _el('a')
strong      = _el('strong')
em          = _el('em')
b           = _el('b')
i           = _el('i')
u           = _el('u')
s           = _el('s')
code        = _el('code')
kbd         = _el('kbd')
mark        = _el('mark')
small       = _el('small')
sub         = _el('sub')
sup         = _el('sup')
label       = _el('label')
abbr        = _el('abbr')
cite        = _el('cite')
q           = _el('q')
time        = _el('time')
bdi         = _el('bdi')
bdo         = _el('bdo')
data        = _el('data')

# ─── Form / interactive ────────────────────────────────────────────────────────
button      = _el('button')
select      = _el('select')
option      = _el('option')
optgroup    = _el('optgroup')
textarea    = _el('textarea')
input       = _el('input')   # shadows builtin; use builtins.input if needed
output      = _el('output')
progress    = _el('progress')
meter       = _el('meter')

# ─── Media / embedding ─────────────────────────────────────────────────────────
img         = _el('img')
video       = _el('video')
audio       = _el('audio')
source      = _el('source')
track       = _el('track')
canvas      = _el('canvas')
iframe      = _el('iframe')
picture     = _el('picture')
svg         = _el('svg')
object_     = _el('object')  # 'object' is a Python builtin
embed       = _el('embed')
map_        = _el('map')     # 'map' is a Python builtin

# ─── Metadata / document ───────────────────────────────────────────────────────
hr          = _el('hr')
br          = _el('br')
link        = _el('link')
meta        = _el('meta')
script      = _el('script')
style       = _el('style')
noscript    = _el('noscript')
template    = _el('template')
slot        = _el('slot')

# ─── Interactive / experimental ────────────────────────────────────────────────
menu        = _el('menu')
