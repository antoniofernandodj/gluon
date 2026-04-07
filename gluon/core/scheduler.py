"""
Update scheduler: batches all pending re-renders into a single DOM pass.

When any use_state setter is called, schedule_rerender() is invoked.
Instead of re-rendering immediately (which would cause multiple renders
per event if several setters fire), we post a single setTimeout(0) and
flush everything in one shot on the next microtask.
"""

from js import setTimeout
from pyodide.ffi import create_proxy

_pending = False
_flush_proxy = None   # lazily created to avoid issues at import time


def _get_proxy():
    global _flush_proxy
    if _flush_proxy is None:
        _flush_proxy = create_proxy(_flush)
    return _flush_proxy


def _flush(*_args):
    global _pending
    _pending = False
    # Import here to avoid circular import at module level
    from gluon.core.renderer import _root_rerender
    _root_rerender()


def schedule_rerender():
    """Request a root re-render on the next event-loop tick."""
    global _pending
    if not _pending:
        _pending = True
        setTimeout(_get_proxy(), 0)
