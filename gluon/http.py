"""
HTTP client using the browser's native fetch API (JS), not Python's urllib/requests.

All network calls go through `window.fetch`, which runs natively in the browser.
The response body is read via JS's `Response.text()` or `Response.json()`.

Usage
-----
    from gluon.http import get, post

    async def load_users():
        resp = await get("https://api.example.com/users")
        print(resp.json())

    async def create_user(name: str):
        resp = await post(
            "https://api.example.com/users",
            json={"name": name},
        )
        print(resp.status)
"""

from __future__ import annotations

from typing import Any, Mapping

from gluon.runtime import fetch as _js_fetch, to_js


# ─── Public types ──────────────────────────────────────────────────────────────

class HttpResponse:
    """
    Thin wrapper around the browser's JS Response object.

    All body-reading methods are async because they call JS Promises
    under the hood (exposed as awaitables in Pyodide).
    """
    __slots__ = ("status", "ok", "status_text", "_js_response")

    def __init__(self, js_resp: Any) -> None:
        self.status: int = js_resp.status
        self.ok: bool = bool(js_resp.ok)
        self.status_text: str = js_resp.statusText
        self._js_response: Any = js_resp

    async def text(self) -> str:
        """Read the full response body as a string."""
        return str(await self._js_response.text())

    async def json(self) -> Any:
        """Parse and return the response body as JSON."""
        import json
        text = await self.text()
        return json.loads(text)

    async def blob(self) -> Any:
        """Return the response body as a JS Blob (useful for images, files, etc.)."""
        return await self._js_response.blob()

    async def array_buffer(self) -> Any:
        """Return the response body as a JS ArrayBuffer."""
        return await self._js_response.arrayBuffer()


# ─── Request helpers ───────────────────────────────────────────────────────────

def _build_init(
    method: str = "GET",
    headers: Mapping[str, str] | None = None,
    body: str | bytes | None = None,
    json: Any = None,
    mode: str | None = None,
    credentials: str | None = None,
    cache: str | None = None,
    signal: Any = None,
) -> dict[str, Any]:
    """
    Build the JS `fetch` init dict from Python-friendly arguments.
    """
    init: dict[str, Any] = {"method": method}

    # Headers
    hdrs: dict[str, str] = dict(headers) if headers else {}
    init["headers"] = hdrs

    # Body
    if json is not None:
        import json as _json_module
        body = _json_module.dumps(json)
        hdrs.setdefault("Content-Type", "application/json")

    if body is not None:
        if isinstance(body, bytes):
            # Pyodide can pass bytes directly to JS via a TypedArray
            init["body"] = to_js(body)
        else:
            init["body"] = body

    # Optional flags
    if mode is not None:
        init["mode"] = mode
    if credentials is not None:
        init["credentials"] = credentials
    if cache is not None:
        init["cache"] = cache
    if signal is not None:
        init["signal"] = signal

    return init


async def request(
    url: str,
    method: str = "GET",
    headers: Mapping[str, str] | None = None,
    body: str | bytes | None = None,
    json: Any = None,
    mode: str | None = None,
    credentials: str | None = None,
    cache: str | None = None,
    signal: Any = None,
) -> HttpResponse:
    """
    Send an HTTP request using the browser's native `fetch` API.

    Parameters
    ----------
    url:
        The full URL to request.
    method:
        HTTP method (GET, POST, PUT, DELETE, PATCH, …).
    headers:
        Extra HTTP headers as a dict.
    body:
        Raw request body (string or bytes).
    json:
        A Python object to serialize as JSON and send as the body.
        Mutually exclusive with `body`.
    mode:
        Fetch mode: "cors", "no-cors", "same-origin".
    credentials:
        Whether to send cookies: "omit", "same-origin", "include".
    cache:
        Cache mode: "default", "no-store", "reload", "no-cache", "force-cache".
    signal:
        An AbortSignal to cancel the request.

    Returns
    -------
    HttpResponse
    """
    init = _build_init(
        method=method,
        headers=headers,
        body=body,
        json=json,
        mode=mode,
        credentials=credentials,
        cache=cache,
        signal=signal,
    )
    js_resp = await _js_fetch(url, init)
    return HttpResponse(js_resp)


# ─── Convenience functions ─────────────────────────────────────────────────────

async def get(url: str, **kwargs: Any) -> HttpResponse:
    """Send a GET request."""
    return await request(url, method="GET", **kwargs)


async def post(url: str, **kwargs: Any) -> HttpResponse:
    """Send a POST request."""
    return await request(url, method="POST", **kwargs)


async def put(url: str, **kwargs: Any) -> HttpResponse:
    """Send a PUT request."""
    return await request(url, method="PUT", **kwargs)


async def patch(url: str, **kwargs: Any) -> HttpResponse:
    """Send a PATCH request."""
    return await request(url, method="PATCH", **kwargs)


async def delete(url: str, **kwargs: Any) -> HttpResponse:
    """Send a DELETE request."""
    return await request(url, method="DELETE", **kwargs)


async def head(url: str, **kwargs: Any) -> HttpResponse:
    """Send a HEAD request."""
    return await request(url, method="HEAD", **kwargs)
