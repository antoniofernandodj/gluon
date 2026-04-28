"""
Update scheduler: batches all pending re-renders into a single DOM pass.

When any use_state setter is called, schedule_rerender() is invoked.
Instead of re-rendering immediately (which would cause multiple renders
per event if several setters fire), we post a single setTimeout(0) and
flush everything in one shot on the next microtask.
"""

from __future__ import annotations

from typing import Any
from gluon.runtime import setTimeout, create_proxy


_pending: bool = False
_flush_proxy: Any | None = None   # lazily created to avoid issues at import time


def _get_proxy() -> Any:
    """Get or create the proxy for the flush function."""
    global _flush_proxy
    if _flush_proxy is None:
        _flush_proxy = create_proxy(_flush)
    return _flush_proxy


def _flush(*_args: Any) -> None:
    """Flush pending renders."""
    global _pending
    _pending = False
    # Import here to avoid circular import at module level
    from gluon.core.renderer import _root_rerender
    _root_rerender()


def schedule_rerender() -> None:
    """Request a root re-render on the next event-loop tick."""
    global _pending
    if not _pending:
        _pending = True
        setTimeout(_get_proxy(), 0)
