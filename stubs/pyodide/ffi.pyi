"""
Type stubs for `pyodide.ffi` — Foreign Function Interface between Python and JS.

Key functions used in Gluon:
  create_proxy  – wraps a Python callable so JS can call it (and keeps it alive)
  to_js         – converts a Python object to its JS equivalent
"""

from typing import Any, Callable, Generic, TypeVar, overload

_T = TypeVar("_T")
_F = TypeVar("_F", bound=Callable[..., Any])

# ── JsProxy ────────────────────────────────────────────────────────────────────

class JsProxy:
    """
    A Python-side handle to a JavaScript object.

    Attribute access, calls, and iteration are forwarded to the underlying
    JS object. Call `.destroy()` when the proxy is no longer needed to
    release the JS-side reference and allow GC.
    """
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
    def destroy(self) -> None: ...
    def to_py(self, **kwargs: Any) -> Any: ...
    def as_object_map(self) -> Any: ...
    def object_entries(self) -> Any: ...
    def object_keys(self) -> Any: ...
    def object_values(self) -> Any: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...  # type: ignore[override]
    def __iter__(self) -> Any: ...
    def __len__(self) -> int: ...
    def __getitem__(self, key: Any) -> Any: ...
    def __setitem__(self, key: Any, value: Any) -> None: ...
    def __contains__(self, item: Any) -> bool: ...
    def __bool__(self) -> bool: ...

# ── Core FFI functions ─────────────────────────────────────────────────────────

def create_proxy(
    obj: _F,
    /,
    *,
    capture_this: bool = ...,
    roundtrip: bool = ...,
) -> JsProxy:
    """
    Wrap *obj* (a Python callable or object) in a JsProxy that JS can call.

    The proxy keeps *obj* alive — call `.destroy()` when done to allow GC.
    Typical usage:

        handler = create_proxy(my_python_fn)
        el.addEventListener("click", handler)
        # later:
        handler.destroy()
    """
    ...

def create_once_callable(obj: _F, /) -> JsProxy:
    """
    Like `create_proxy`, but the proxy destroys itself after the first call.
    """
    ...

def to_js(
    obj: Any,
    /,
    *,
    depth: int = ...,
    pyproxies: Any = ...,
    create_pyproxies: bool = ...,
    dict_converter: Any = ...,
    default_converter: Any = ...,
) -> JsProxy:
    """
    Convert a Python object to a JavaScript object.

    Dicts become JS objects, lists/tuples become JS Arrays, etc.
    """
    ...

def from_js(obj: Any, /) -> Any:
    """Convert a JavaScript object to a Python object (inverse of to_js)."""
    ...

def destroy_proxies(proxies: list[JsProxy], /) -> None:
    """Destroy a list of proxies in bulk."""
    ...

# ── Python↔JS callable wrappers ────────────────────────────────────────────────

class ConvertibleToJs:
    def to_js(self, **kwargs: Any) -> JsProxy: ...

class JsBuffer(JsProxy):
    """Proxy for ArrayBuffer / TypedArray objects."""
    def to_py(self, **kwargs: Any) -> Any: ...  # returns memoryview or ndarray
    @property
    def byteLength(self) -> int: ...
    @property
    def byteOffset(self) -> int: ...
