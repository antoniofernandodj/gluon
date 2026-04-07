"""
Type stubs for the `js` module available inside PyScript / Pyodide.

The `js` module exposes the browser's global JavaScript namespace.
Everything here is a Python-visible projection of the Web APIs; the
actual objects are JS-backed JsProxy instances at runtime.
"""

from typing import Any, overload

# ── Low-level proxy base ───────────────────────────────────────────────────────

class JsProxy:
    """Generic proxy for any JavaScript object."""
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
    def destroy(self) -> None: ...
    def to_py(self, **kwargs: Any) -> Any: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def __iter__(self) -> Any: ...
    def __len__(self) -> int: ...
    def __getitem__(self, key: Any) -> Any: ...
    def __setitem__(self, key: Any, value: Any) -> None: ...

# ── CSS / Style ────────────────────────────────────────────────────────────────

class CSSStyleDeclaration:
    """el.style — inline CSS on a DOM element."""
    cssText: str
    # A selection of common properties; __getattr__ covers the rest.
    color: str
    background: str
    backgroundColor: str
    border: str
    borderRadius: str
    borderTop: str
    borderBottom: str
    borderLeft: str
    borderRight: str
    margin: str
    marginTop: str
    marginBottom: str
    marginLeft: str
    marginRight: str
    padding: str
    paddingTop: str
    paddingBottom: str
    paddingLeft: str
    paddingRight: str
    width: str
    height: str
    minWidth: str
    maxWidth: str
    minHeight: str
    maxHeight: str
    display: str
    flexDirection: str
    flexWrap: str
    flex: str
    alignItems: str
    alignSelf: str
    justifyContent: str
    justifySelf: str
    gap: str
    position: str
    top: str
    bottom: str
    left: str
    right: str
    zIndex: str
    overflow: str
    overflowX: str
    overflowY: str
    opacity: str
    visibility: str
    cursor: str
    pointerEvents: str
    fontFamily: str
    fontSize: str
    fontWeight: str
    fontStyle: str
    lineHeight: str
    letterSpacing: str
    textAlign: str
    textDecoration: str
    textTransform: str
    listStyle: str
    boxSizing: str
    boxShadow: str
    transform: str
    transition: str
    animation: str
    gridTemplateColumns: str
    gridTemplateRows: str
    gridColumn: str
    gridRow: str
    inset: str
    def getPropertyValue(self, prop: str) -> str: ...
    def setProperty(self, prop: str, value: str, priority: str = ...) -> None: ...
    def removeProperty(self, prop: str) -> str: ...
    def __getattr__(self, name: str) -> str: ...
    def __setattr__(self, name: str, value: str) -> None: ...  # type: ignore[override]

# ── DOM Events ─────────────────────────────────────────────────────────────────

class Event:
    type: str
    target: "Element"
    currentTarget: "Element"
    bubbles: bool
    cancelable: bool
    defaultPrevented: bool
    timeStamp: float
    def preventDefault(self) -> None: ...
    def stopPropagation(self) -> None: ...
    def stopImmediatePropagation(self) -> None: ...
    def __getattr__(self, name: str) -> Any: ...

class UIEvent(Event):
    detail: int
    view: Any

class MouseEvent(UIEvent):
    clientX: float
    clientY: float
    pageX: float
    pageY: float
    screenX: float
    screenY: float
    offsetX: float
    offsetY: float
    movementX: float
    movementY: float
    button: int
    buttons: int
    altKey: bool
    ctrlKey: bool
    shiftKey: bool
    metaKey: bool
    relatedTarget: "Element | None"

class KeyboardEvent(UIEvent):
    key: str
    code: str
    keyCode: int
    charCode: int
    which: int
    altKey: bool
    ctrlKey: bool
    shiftKey: bool
    metaKey: bool
    repeat: bool
    isComposing: bool
    def getModifierState(self, key: str) -> bool: ...

class InputEvent(UIEvent):
    data: str | None
    inputType: str
    isComposing: bool

class FocusEvent(UIEvent):
    relatedTarget: "Element | None"

class WheelEvent(MouseEvent):
    deltaX: float
    deltaY: float
    deltaZ: float
    deltaMode: int

class DragEvent(MouseEvent):
    dataTransfer: Any

class TouchEvent(UIEvent):
    touches: Any
    targetTouches: Any
    changedTouches: Any
    altKey: bool
    ctrlKey: bool
    shiftKey: bool
    metaKey: bool

class SubmitEvent(Event):
    submitter: "Element | None"

# ── DOM Nodes ──────────────────────────────────────────────────────────────────

class Node:
    nodeType: int
    nodeName: str
    nodeValue: str | None
    textContent: str | None
    parentNode: "Node | None"
    parentElement: "Element | None"
    childNodes: Any
    firstChild: "Node | None"
    lastChild: "Node | None"
    nextSibling: "Node | None"
    previousSibling: "Node | None"
    ownerDocument: "Document"
    def appendChild(self, node: "Node") -> "Node": ...
    def removeChild(self, node: "Node") -> "Node": ...
    def insertBefore(self, newNode: "Node", refNode: "Node | None") -> "Node": ...
    def replaceChild(self, newNode: "Node", oldNode: "Node") -> "Node": ...
    def cloneNode(self, deep: bool = ...) -> "Node": ...
    def contains(self, other: "Node | None") -> bool: ...
    def hasChildNodes(self) -> bool: ...

class Element(Node):
    tagName: str
    id: str
    className: str
    classList: Any
    innerHTML: str
    outerHTML: str
    textContent: str
    style: CSSStyleDeclaration
    children: Any           # HTMLCollection — iterate or index as needed
    firstElementChild: "Element | None"
    lastElementChild: "Element | None"
    nextElementSibling: "Element | None"
    previousElementSibling: "Element | None"
    childElementCount: int
    scrollTop: float
    scrollLeft: float
    scrollWidth: int
    scrollHeight: int
    clientWidth: int
    clientHeight: int
    offsetWidth: int
    offsetHeight: int
    offsetTop: int
    offsetLeft: int
    def getAttribute(self, name: str) -> str | None: ...
    def setAttribute(self, name: str, value: str) -> None: ...
    def removeAttribute(self, name: str) -> None: ...
    def hasAttribute(self, name: str) -> bool: ...
    def toggleAttribute(self, name: str, force: bool = ...) -> bool: ...
    def querySelector(self, selector: str) -> "Element | None": ...
    def querySelectorAll(self, selector: str) -> Any: ...
    def closest(self, selector: str) -> "Element | None": ...
    def matches(self, selector: str) -> bool: ...
    def addEventListener(self, type: str, listener: Any, options: Any = ...) -> None: ...
    def removeEventListener(self, type: str, listener: Any, options: Any = ...) -> None: ...
    def dispatchEvent(self, event: Event) -> bool: ...
    def getBoundingClientRect(self) -> Any: ...
    def scrollIntoView(self, options: Any = ...) -> None: ...
    def remove(self) -> None: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...  # type: ignore[override]

class HTMLElement(Element):
    title: str
    lang: str
    hidden: bool
    tabIndex: int
    draggable: bool
    contentEditable: str
    isContentEditable: bool
    offsetParent: "Element | None"
    def click(self) -> None: ...
    def focus(self, options: Any = ...) -> None: ...
    def blur(self) -> None: ...

class HTMLInputElement(HTMLElement):
    type: str
    name: str
    value: str
    defaultValue: str
    checked: bool
    defaultChecked: bool
    indeterminate: bool
    disabled: bool
    readOnly: bool
    required: bool
    placeholder: str
    min: str
    max: str
    step: str
    minLength: int
    maxLength: int
    pattern: str
    multiple: bool
    accept: str
    selectionStart: int | None
    selectionEnd: int | None
    selectionDirection: str | None
    files: Any
    def select(self) -> None: ...
    def setSelectionRange(self, start: int, end: int, direction: str = ...) -> None: ...
    def setRangeText(self, replacement: str, start: int = ..., end: int = ..., selectMode: str = ...) -> None: ...
    def checkValidity(self) -> bool: ...
    def reportValidity(self) -> bool: ...

class HTMLTextAreaElement(HTMLElement):
    value: str
    defaultValue: str
    disabled: bool
    readOnly: bool
    required: bool
    placeholder: str
    rows: int
    cols: int
    minLength: int
    maxLength: int
    selectionStart: int
    selectionEnd: int
    def select(self) -> None: ...
    def setSelectionRange(self, start: int, end: int, direction: str = ...) -> None: ...

class HTMLSelectElement(HTMLElement):
    value: str
    selectedIndex: int
    disabled: bool
    required: bool
    multiple: bool
    size: int
    options: Any
    selectedOptions: Any
    length: int
    def add(self, element: Any, before: Any = ...) -> None: ...
    def remove(self, index: int) -> None: ...

class HTMLFormElement(HTMLElement):
    method: str
    action: str
    enctype: str
    noValidate: bool
    def submit(self) -> None: ...
    def reset(self) -> None: ...
    def checkValidity(self) -> bool: ...
    def reportValidity(self) -> bool: ...

class HTMLAnchorElement(HTMLElement):
    href: str
    target: str
    rel: str
    download: str
    hash: str
    host: str
    hostname: str
    pathname: str
    search: str

class HTMLImageElement(HTMLElement):
    src: str
    alt: str
    width: int
    height: int
    naturalWidth: int
    naturalHeight: int
    complete: bool

class DocumentFragment(Node):
    def querySelector(self, selector: str) -> Element | None: ...
    def querySelectorAll(self, selector: str) -> Any: ...
    def appendChild(self, node: Node) -> Node: ...

# ── Document ───────────────────────────────────────────────────────────────────

class Document(Node):
    activeElement: HTMLElement | None
    body: HTMLElement
    documentElement: HTMLElement
    head: HTMLElement
    title: str
    URL: str
    readyState: str
    cookie: str
    def createElement(self, tagName: str) -> HTMLElement: ...
    def createElementNS(self, ns: str, tagName: str) -> Element: ...
    def createTextNode(self, data: str) -> Node: ...
    def createDocumentFragment(self) -> DocumentFragment: ...
    def createEvent(self, eventInterface: str) -> Event: ...
    def getElementById(self, id: str) -> HTMLElement | None: ...
    def querySelector(self, selector: str) -> HTMLElement | None: ...
    def querySelectorAll(self, selector: str) -> Any: ...
    def getElementsByTagName(self, tag: str) -> Any: ...
    def getElementsByClassName(self, names: str) -> Any: ...
    def addEventListener(self, type: str, listener: Any, options: Any = ...) -> None: ...
    def removeEventListener(self, type: str, listener: Any, options: Any = ...) -> None: ...
    def dispatchEvent(self, event: Event) -> bool: ...
    def __getattr__(self, name: str) -> Any: ...

# ── Location / History ─────────────────────────────────────────────────────────

class Location:
    href: str
    origin: str
    protocol: str
    host: str
    hostname: str
    port: str
    pathname: str
    search: str
    hash: str
    def assign(self, url: str) -> None: ...
    def replace(self, url: str) -> None: ...
    def reload(self) -> None: ...

class History:
    length: int
    state: Any
    scrollRestoration: str
    def back(self) -> None: ...
    def forward(self) -> None: ...
    def go(self, delta: int = ...) -> None: ...
    def pushState(self, state: Any, title: str, url: str = ...) -> None: ...
    def replaceState(self, state: Any, title: str, url: str = ...) -> None: ...

# ── Console ────────────────────────────────────────────────────────────────────

class Console:
    def log(self, *args: Any) -> None: ...
    def warn(self, *args: Any) -> None: ...
    def error(self, *args: Any) -> None: ...
    def info(self, *args: Any) -> None: ...
    def debug(self, *args: Any) -> None: ...
    def table(self, data: Any) -> None: ...
    def group(self, *args: Any) -> None: ...
    def groupEnd(self) -> None: ...
    def time(self, label: str) -> None: ...
    def timeEnd(self, label: str) -> None: ...
    def clear(self) -> None: ...

# ── Window ─────────────────────────────────────────────────────────────────────

class Window:
    document: Document
    location: Location
    history: History
    console: Console
    navigator: Any
    screen: Any
    innerWidth: int
    innerHeight: int
    outerWidth: int
    outerHeight: int
    scrollX: float
    scrollY: float
    devicePixelRatio: float
    performance: Any
    localStorage: Any
    sessionStorage: Any
    indexedDB: Any
    crypto: Any
    def setTimeout(self, handler: Any, delay: int = ..., *args: Any) -> int: ...
    def clearTimeout(self, id: int) -> None: ...
    def setInterval(self, handler: Any, delay: int = ..., *args: Any) -> int: ...
    def clearInterval(self, id: int) -> None: ...
    def requestAnimationFrame(self, callback: Any) -> int: ...
    def cancelAnimationFrame(self, id: int) -> None: ...
    def fetch(self, input: Any, init: Any = ...) -> Any: ...
    def alert(self, message: str = ...) -> None: ...
    def confirm(self, message: str = ...) -> bool: ...
    def prompt(self, message: str = ..., default: str = ...) -> str | None: ...
    def open(self, url: str = ..., target: str = ..., features: str = ...) -> "Window | None": ...
    def close(self) -> None: ...
    def scrollTo(self, x: float, y: float) -> None: ...
    def scrollBy(self, x: float, y: float) -> None: ...
    def addEventListener(self, type: str, listener: Any, options: Any = ...) -> None: ...
    def removeEventListener(self, type: str, listener: Any, options: Any = ...) -> None: ...
    def dispatchEvent(self, event: Event) -> bool: ...
    def __getattr__(self, name: str) -> Any: ...

# ── Module-level globals ───────────────────────────────────────────────────────

document: Document
window: Window
location: Location
history: History
console: Console
navigator: Any
screen: Any
performance: Any
localStorage: Any
sessionStorage: Any
crypto: Any
Object: Any
JSON: Any
Array: Any
Math: Any
Date: Any
Promise: Any
Error: Any
fetch: Any

def setTimeout(handler: Any, delay: int = ..., *args: Any) -> int: ...
def clearTimeout(id: int = ...) -> None: ...
def setInterval(handler: Any, delay: int = ..., *args: Any) -> int: ...
def clearInterval(id: int = ...) -> None: ...
def requestAnimationFrame(callback: Any) -> int: ...
def cancelAnimationFrame(id: int) -> None: ...
def alert(message: str = ...) -> None: ...
def confirm(message: str = ...) -> bool: ...
def prompt(message: str = ..., default: str = ...) -> str | None: ...
