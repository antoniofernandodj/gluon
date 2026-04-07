"""
Gluon — A React-inspired Python UI framework for the browser via WebAssembly.

Quick start
-----------
    from gluon import component, use_state, render
    from gluon import div, h1, p, button
    from js import document

    @component
    def Counter():
        count, set_count = use_state(0)
        return div(
            h1('Gluon'),
            p(f'Count: {count}'),
            button('-', onClick=lambda e: set_count(count - 1)),
            button('+', onClick=lambda e: set_count(count + 1)),
        )

    render(Counter, document.getElementById('root'))
"""

# ── Core API ──────────────────────────────────────────────────────────────────
from gluon.core.component import component, Component
from gluon.core.hooks import use_state
from gluon.core.renderer import render

# ── HTTP client (browser native fetch) ────────────────────────────────────────
from gluon.http import (
    HttpResponse,
    request,
    get,
    post,
    put,
    patch,
    delete,
    head,
)

# ── HTML elements ─────────────────────────────────────────────────────────────
from gluon.core.vdom import (
    fragment,
    # Block / structural
    div, p, section, article, aside, header, footer, main, nav,
    ul, ol, li, dl, dt, dd,
    table, thead, tbody, tfoot, tr, th, td,
    form, fieldset, legend,
    details, summary, dialog,
    figure, figcaption,
    blockquote, pre, address,
    # Headings
    h1, h2, h3, h4, h5, h6,
    # Inline
    span, a, strong, em, b, i, u, s, code, kbd, mark,
    small, sub, sup, label, abbr, cite, q, time, bdi, bdo, data,
    # Form / interactive
    button, select, option, optgroup, textarea, input,
    output, progress, meter,
    # Media / embedding
    img, video, audio, source, track, canvas, iframe, picture, svg,
    object_, embed, map_,
    # Misc
    hr, br, link, meta, script, style, noscript, template, slot, menu,
)

__all__ = [
    # Core
    'component', 'Component', 'use_state', 'render', 'fragment',
    # HTTP
    'HttpResponse', 'request', 'get', 'post', 'put', 'patch', 'delete', 'head',
    # Block
    'div', 'p', 'section', 'article', 'aside', 'header', 'footer',
    'main', 'nav', 'ul', 'ol', 'li', 'dl', 'dt', 'dd',
    'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td',
    'form', 'fieldset', 'legend', 'details', 'summary', 'dialog',
    'figure', 'figcaption', 'blockquote', 'pre', 'address',
    # Headings
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    # Inline
    'span', 'a', 'strong', 'em', 'b', 'i', 'u', 's', 'code', 'kbd',
    'mark', 'small', 'sub', 'sup', 'label', 'abbr', 'cite', 'q',
    'time', 'bdi', 'bdo', 'data',
    # Form
    'button', 'select', 'option', 'optgroup', 'textarea', 'input',
    'output', 'progress', 'meter',
    # Media
    'img', 'video', 'audio', 'source', 'track', 'canvas', 'iframe',
    'picture', 'svg', 'object_', 'embed', 'map_',
    # Misc
    'hr', 'br', 'link', 'meta', 'script', 'style', 'noscript',
    'template', 'slot', 'menu',
]
