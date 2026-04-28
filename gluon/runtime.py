import sys
from typing import Any

# Detect if we are running inside Pyodide (browser)
IS_BROWSER = "pyodide" in sys.modules or "js" in sys.modules

# Default stubs for server-side or before initialization
def _stub_fn(*args: Any, **kwargs: Any) -> Any:
    return None

class Mock:
    """A mock object that returns a stub function for any attribute access."""
    def __getattr__(self, name: str) -> Any:
        return _stub_fn
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return None

if IS_BROWSER:
    try:
        from js import document, window, setTimeout, fetch
        from pyodide.ffi import create_proxy, to_js
    except ImportError:
        document = Mock()
        window = Mock()
        setTimeout = _stub_fn
        fetch = _stub_fn
        create_proxy = _stub_fn
        to_js = _stub_fn
else:
    # On server, provide Mocks to satisfy static analysis
    document = Mock()
    window = Mock()
    setTimeout = _stub_fn
    fetch = _stub_fn
    create_proxy = _stub_fn
    to_js = _stub_fn


def is_server() -> bool:
    return not IS_BROWSER


def is_browser() -> bool:
    return IS_BROWSER
