"""
DOM Renderer — Phase 1.

Strategy: full tree replacement on every state update.
  • create_dom()       – recursively turn a VNode tree into real DOM nodes
  • render()           – mount a root component into a container element
  • _root_rerender()   – called by the scheduler to flush pending updates

Phase 2 will replace the innerHTML-clear approach with a keyed diffing
reconciler so only changed nodes are patched.

Event handling
--------------
Python callables passed as event props (onClick, onChange, …) are wrapped
in a create_proxy() before being handed to addEventListener.  All proxies
are stored in _active_proxies and destroyed before each re-render to
prevent memory leaks.

Prop normalisation
------------------
- class_ / className   → class
- for_ / htmlFor       → for
- style as dict        → el.style.<property> = value  (camelCase or kebab)
- bool attributes      → setAttribute(attr, '') / removeAttribute
"""

import inspect

from js import document
from pyodide.ffi import create_proxy

import gluon.core.fiber as _ctx
from gluon.core.fiber import Fiber
from gluon.core.vdom import VNode, FragmentNode
from gluon.core.component import Component


# ─── Root state ────────────────────────────────────────────────────────────────
_root_fiber: Fiber | None = None
_root_container = None       # JS DOM element

# ─── Per-component fiber registry (Phase 1: one fiber per component fn) ───────
_fiber_registry: dict = {}

# ─── Live JS proxies (destroyed before each re-render) ────────────────────────
_active_proxies: list = []


# ─── Event name map ────────────────────────────────────────────────────────────
_EVENT_MAP: dict[str, str] = {
    'onClick':       'click',
    'onDblClick':    'dblclick',
    'onChange':      'change',
    'onInput':       'input',
    'onSubmit':      'submit',
    'onReset':       'reset',
    'onKeyDown':     'keydown',
    'onKeyUp':       'keyup',
    'onKeyPress':    'keypress',
    'onMouseDown':   'mousedown',
    'onMouseUp':     'mouseup',
    'onMouseEnter':  'mouseenter',
    'onMouseLeave':  'mouseleave',
    'onMouseMove':   'mousemove',
    'onMouseOver':   'mouseover',
    'onMouseOut':    'mouseout',
    'onFocus':       'focus',
    'onBlur':        'blur',
    'onScroll':      'scroll',
    'onWheel':       'wheel',
    'onContextMenu': 'contextmenu',
    'onDragStart':   'dragstart',
    'onDragEnd':     'dragend',
    'onDragOver':    'dragover',
    'onDrop':        'drop',
    'onTouchStart':  'touchstart',
    'onTouchEnd':    'touchend',
    'onTouchMove':   'touchmove',
    'onLoad':        'load',
    'onError':       'error',
}
# Also accept lowercase variants: onclick, onchange, …
for _k, _v in list(_EVENT_MAP.items()):
    _EVENT_MAP[_k.lower()] = _v

# ─── Prop name map ─────────────────────────────────────────────────────────────
_PROP_MAP: dict[str, str] = {
    'class_':      'class',
    'className':   'class',
    'htmlFor':     'for',
    'for_':        'for',
    'tabIndex':    'tabindex',
    'readOnly':    'readonly',
    'autoFocus':   'autofocus',
    'autoPlay':    'autoplay',
    'crossOrigin': 'crossorigin',
    'srcSet':      'srcset',
    'useMap':      'usemap',
    'maxLength':   'maxlength',
    'minLength':   'minlength',
    'colSpan':     'colspan',
    'rowSpan':     'rowspan',
}

# ─── Void elements (no children) ───────────────────────────────────────────────
_VOID: frozenset[str] = frozenset({
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr',
})


# ─── CSS kebab → camelCase ─────────────────────────────────────────────────────
def _css_key(name: str) -> str:
    parts = name.split('-')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])


# ─── DOM creation ──────────────────────────────────────────────────────────────

def create_dom(vnode, proxies: list):
    """Recursively convert a VNode tree to real DOM nodes."""

    if vnode is None or vnode is False:
        return None

    # Text nodes
    if isinstance(vnode, (str, int, float)):
        return document.createTextNode(str(vnode))

    if isinstance(vnode, bool):
        return None  # False already handled; True rendered as 'True' would be odd

    # Fragment
    if isinstance(vnode, FragmentNode):
        frag = document.createDocumentFragment()
        for child in vnode.children:
            node = create_dom(child, proxies)
            if node is not None:
                frag.appendChild(node)
        return frag

    # Lists / tuples (e.g. from list comprehensions in JSX position)
    if isinstance(vnode, (list, tuple)):
        frag = document.createDocumentFragment()
        for item in vnode:
            node = create_dom(item, proxies)
            if node is not None:
                frag.appendChild(node)
        return frag

    if isinstance(vnode, VNode):
        tag = vnode.type

        # ── Component VNode ───────────────────────────────────────────────
        if callable(tag):
            return _expand_component(vnode, proxies)

        # ── Regular DOM element ───────────────────────────────────────────
        el = document.createElement(tag)
        _apply_props(el, vnode.props, proxies)

        if tag not in _VOID:
            for child in vnode.children:
                node = create_dom(child, proxies)
                if node is not None:
                    el.appendChild(node)

        return el

    # Fallback: stringify anything else
    return document.createTextNode(str(vnode))


def _apply_props(el, props: dict, proxies: list) -> None:
    for key, val in props.items():
        if val is None:
            continue

        # Events ──────────────────────────────────────────────────────────
        if key in _EVENT_MAP:
            proxy = create_proxy(val)
            proxies.append(proxy)
            el.addEventListener(_EVENT_MAP[key], proxy)
            continue

        # style dict ──────────────────────────────────────────────────────
        if key == 'style' and isinstance(val, dict):
            for s_key, s_val in val.items():
                setattr(el.style, _css_key(s_key), str(s_val))
            continue

        # dangerouslySetInnerHTML ─────────────────────────────────────────
        if key == 'dangerouslySetInnerHTML' and isinstance(val, dict):
            el.innerHTML = val.get('__html', '')
            continue

        # skip internal keys
        if key == 'children':
            continue

        dom_attr = _PROP_MAP.get(key, key)

        if isinstance(val, bool):
            if val:
                el.setAttribute(dom_attr, '')
            # False → omit attribute
        else:
            el.setAttribute(dom_attr, str(val))


# ─── Component expansion ───────────────────────────────────────────────────────

def _expand_component(vnode: VNode, proxies: list):
    """Render a component VNode: set fiber context, call fn, recurse."""
    tag = vnode.type
    props = dict(vnode.props)
    children = props.pop('children', vnode.children or [])

    # ── Class-based component ─────────────────────────────────────────────
    if isinstance(tag, type) and issubclass(tag, Component):
        instance = tag.__new__(tag)
        instance.props = {**props, 'children': children}
        instance.__init__(**props)
        result = instance.render()
        return create_dom(result, proxies)

    # ── Functional component ──────────────────────────────────────────────
    if tag not in _fiber_registry:
        _fiber_registry[tag] = Fiber(tag)
    fiber = _fiber_registry[tag]

    prev = _ctx._current_fiber
    _ctx._current_fiber = fiber
    fiber.hook_index = 0
    try:
        result = _call_fn(tag, props, children)
    finally:
        _ctx._current_fiber = prev

    return create_dom(result, proxies)


def _call_fn(fn, props: dict, children: list):
    """
    Call *fn* passing only the parameters it actually declares.

    Calling conventions supported:
      def Comp()                      – no args
      def Comp(text, color='red')     – positional params filled from children
      def Comp(children=None, **p)    – children keyword + extra props
      def Comp(*children, **props)    – var-positional + var-keyword
      def Comp(*children, class_=…)   – var-positional + keyword-only
    """
    sig = inspect.signature(fn)
    params = sig.parameters

    has_var_kw  = any(p.kind == inspect.Parameter.VAR_KEYWORD  for p in params.values())
    has_var_pos = any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in params.values())

    # def Comp(*children, **props)  →  pass children positionally, rest as kwargs
    if has_var_pos and has_var_kw:
        return fn(*children, **props)

    # def Comp(**props)  →  inject children into props
    if has_var_kw:
        kwargs = dict(props)
        kwargs.setdefault('children', children)
        return fn(**kwargs)

    # def Comp(*children, class_=…)  →  children go positionally, keyword-only as kwargs
    if has_var_pos:
        kw_only = {
            name: props[name]
            for name, param in params.items()
            if param.kind == inspect.Parameter.KEYWORD_ONLY and name in props
        }
        return fn(*children, **kw_only)

    # def Comp(text, title, color='…')  →  named params filled from props first,
    # then from children in declaration order for any that are still missing.
    kwargs: dict = {}
    children_iter = iter(children)

    for name, param in params.items():
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        if name in props:
            kwargs[name] = props[name]
        elif name == 'children':
            kwargs['children'] = children
        elif param.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ):
            # Fill missing positional params from children (in order)
            try:
                kwargs[name] = next(children_iter)
            except StopIteration:
                pass  # will raise naturally if the param is required

    return fn(**kwargs)


# ─── Root render ───────────────────────────────────────────────────────────────

def render(component_wrapper, container):
    """
    Mount a root component into a DOM container element.

    Parameters
    ----------
    component_wrapper:
        A function decorated with @component, or a Component subclass.
    container:
        A JS DOM element (e.g. document.getElementById('root')).
    """
    global _root_fiber, _root_container

    # Unwrap @component wrapper to get the original function
    fn = getattr(component_wrapper, '_component_fn', component_wrapper)

    if fn not in _fiber_registry:
        _fiber_registry[fn] = Fiber(fn)

    _root_fiber = _fiber_registry[fn]
    _root_container = container

    _do_render()


def _root_rerender():
    """Called by the scheduler after batching state updates."""
    _do_render()


def _do_render():
    global _active_proxies

    if _root_fiber is None or _root_container is None:
        return

    # Destroy old JS proxies to avoid memory leaks
    for proxy in _active_proxies:
        try:
            proxy.destroy()
        except Exception:
            pass

    proxies: list = []

    # Render root component with its fiber as context
    prev = _ctx._current_fiber
    _ctx._current_fiber = _root_fiber
    _root_fiber.hook_index = 0
    try:
        vnode = _root_fiber.component_fn()
    finally:
        _ctx._current_fiber = prev

    dom_node = create_dom(vnode, proxies)

    # Replace container content atomically
    _root_container.innerHTML = ''
    if dom_node is not None:
        _root_container.appendChild(dom_node)

    _active_proxies = proxies
