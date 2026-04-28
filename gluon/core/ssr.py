"""
SSR Renderer — Server-Side Rendering for Gluon.

Converts a VNode tree into a static HTML string.
This is used by the server to send a pre-rendered page to the browser.
"""

from __future__ import annotations

import html
from typing import Any, Callable, cast

from gluon.core.vdom import VNode, FragmentNode
from gluon.core.component import Component
from gluon.core.renderer import _call_fn, _PROP_MAP, _VOID, _css_key
import gluon.core.fiber as _ctx
from gluon.core.fiber import Fiber

# Mock registry for SSR (single pass, no persistence needed usually)
_ssr_fiber_registry: dict[Callable[..., Any], Fiber] = {}

def render_to_static_markup(vnode: Any) -> str:
    """
    Recursively convert a VNode tree into an HTML string.
    """
    if vnode is None or vnode is False:
        return ""

    if isinstance(vnode, (str, int, float)):
        return html.escape(str(vnode))

    if isinstance(vnode, bool):
        return ""

    if isinstance(vnode, FragmentNode):
        return "".join(render_to_static_markup(child) for child in vnode.children)

    if isinstance(vnode, (list, tuple)):
        return "".join(render_to_static_markup(item) for item in vnode)

    if isinstance(vnode, VNode):
        tag = vnode.type

        # ── Component VNode ───────────────────────────────────────────────
        if callable(tag):
            return _expand_component_ssr(vnode)

        # ── Regular DOM element ───────────────────────────────────────────
        props_str = _render_props_ssr(vnode.props)
        
        if tag in _VOID:
            return f"<{tag}{props_str}>"
        
        children_html = "".join(render_to_static_markup(child) for child in vnode.children)
        
        # Handle dangerouslySetInnerHTML
        if 'dangerouslySetInnerHTML' in vnode.props:
            children_html = vnode.props['dangerouslySetInnerHTML'].get('__html', '')

        return f"<{tag}{props_str}>{children_html}</{tag}>"

    return html.escape(str(vnode))


def _render_props_ssr(props: dict[str, Any]) -> str:
    """Convert props dict to a string of HTML attributes."""
    parts = []
    
    for key, val in props.items():
        if val is None or key == 'children' or key == 'dangerouslySetInnerHTML':
            continue
            
        # Skip events on server
        if key.lower().startswith('on') and callable(val):
            continue

        if key == 'style' and isinstance(val, dict):
            style_parts = []
            for s_key, s_val in val.items():
                # Convert camelCase to kebab-case for CSS
                kebab_key = ''.join(['-' + c.lower() if c.isupper() else c for c in s_key]).lstrip('-')
                style_parts.append(f"{kebab_key}: {s_val}")
            if style_parts:
                parts.append(f' style="{html.escape("; ".join(style_parts))}"')
            continue

        attr_name = _PROP_MAP.get(key, key)
        
        if isinstance(val, bool):
            if val:
                parts.append(f' {attr_name}')
        else:
            parts.append(f' {attr_name}="{html.escape(str(val))}"')
            
    return "".join(parts)


# Registry for SSR hydration data
_ssr_hydration_data: dict[str, str] = {}

def get_hydration_data() -> dict[str, str]:
    return _ssr_hydration_data

def _expand_component_ssr(vnode: VNode) -> str:
    """Render a component VNode to HTML string."""
    tag = vnode.type
    props = dict(vnode.props)
    children = props.pop('children', vnode.children or [])

    # ── Class-based component ─────────────────────────────────────────────
    if isinstance(tag, type) and issubclass(tag, Component):
        instance = tag.__new__(tag)
        instance.props = {**props, 'children': children}
        instance.__init__(**props)
        result = instance.render()
        return render_to_static_markup(result)

    # ── Functional component ──────────────────────────────────────────────
    fn = cast(Callable[..., Any], tag)
    
    # Check if it's a server component
    is_server_comp = getattr(fn, "_is_server_component", False)
    # Use only __name__ for the ID to be stable across different module naming (app vs __main__)
    comp_id = fn.__name__
    
    if fn not in _ssr_fiber_registry:
        _ssr_fiber_registry[fn] = Fiber(fn)
    fiber = _ssr_fiber_registry[fn]

    prev = _ctx._current_fiber
    _ctx._current_fiber = fiber
    fiber.hook_index = 0
    try:
        result = _call_fn(fn, props, children)
    finally:
        _ctx._current_fiber = prev

    html_output = render_to_static_markup(result)
    
    # Wrap server components in a marker and save hydration data
    if is_server_comp:
        _ssr_hydration_data[comp_id] = html_output
        return f'<!-- gluon-s:{comp_id} -->{html_output}<!-- gluon-e -->'
    
    return html_output
