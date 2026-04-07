"""Type stubs for `pyodide.http` — HTTP utilities in Pyodide."""

from typing import Any

class FetchResponse:
    status: int
    ok: bool
    redirected: bool
    headers: Any
    url: str
    def string(self) -> Any: ...   # awaitable → str
    def json(self) -> Any: ...     # awaitable → Any
    def bytes(self) -> Any: ...    # awaitable → bytes
    def buffer(self) -> Any: ...   # awaitable → JsProxy (ArrayBuffer)

async def pyfetch(url: str, **kwargs: Any) -> FetchResponse: ...
