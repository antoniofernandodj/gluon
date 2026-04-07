# HTTP Client

`gluon.http` is a thin wrapper around the browser's native `window.fetch` API.
All requests run through the browser — no Python `urllib` or `requests` library
is involved. This means:

- No WASM-side network stack to configure.
- Requests inherit the browser's cookie jar, CORS rules, and security policies.
- The API surface is intentionally close to Python's `requests` library.

---

## Quick start

```python
from gluon import component, use_state, div, button, ul, li, p
from gluon.http import get

@component
def UserList():
    users,   set_users   = use_state([])
    loading, set_loading = use_state(False)
    error,   set_error   = use_state("")

    async def fetch_users(e):
        set_loading(True)
        set_error("")
        try:
            resp = await get("https://jsonplaceholder.typicode.com/users?_limit=5")
            if resp.ok:
                set_users(await resp.json())
            else:
                set_error(f"Error {resp.status}: {resp.status_text}")
        except Exception as exc:
            set_error(str(exc))
        finally:
            set_loading(False)

    return div(
        button("Load users", onClick=fetch_users),
        p("Loading…", style={"color": "#888"}) if loading else None,
        p(error, style={"color": "#e74c3c"}) if error else None,
        ul(*[
            li(f'{user["name"]} — {user["email"]}')
            for user in users
        ]) if users else None,
    )
```

---

## Functions

All functions are `async` and must be awaited inside an `async def` handler.

### `get(url, **kwargs) → HttpResponse`

```python
resp = await get("https://api.example.com/users")
resp = await get("https://api.example.com/users", headers={"Accept": "application/json"})
```

### `post(url, **kwargs) → HttpResponse`

```python
resp = await post("https://api.example.com/items", json={"name": "widget"})
resp = await post("https://api.example.com/upload", body=raw_bytes)
```

### `put(url, **kwargs) → HttpResponse`

```python
resp = await put("https://api.example.com/items/42", json={"name": "updated"})
```

### `patch(url, **kwargs) → HttpResponse`

```python
resp = await patch("https://api.example.com/items/42", json={"qty": 5})
```

### `delete(url, **kwargs) → HttpResponse`

```python
resp = await delete("https://api.example.com/items/42")
```

### `head(url, **kwargs) → HttpResponse`

```python
resp = await head("https://api.example.com/file.zip")
size = resp.status   # check headers without downloading the body
```

### `request(url, method, **kwargs) → HttpResponse`

Full-control function used internally by all the above:

```python
resp = await request(
    "https://api.example.com/data",
    method="GET",
    headers={"Authorization": "Bearer token"},
    mode="cors",
    credentials="include",
    cache="no-store",
)
```

---

## Keyword arguments

All convenience functions (`get`, `post`, …) forward `**kwargs` to `request`.

| Argument | Type | Description |
| -------- | ---- | ----------- |
| `headers` | `dict[str, str]` | Extra HTTP headers |
| `body` | `str \| bytes` | Raw request body |
| `json` | `Any` | Serialised as JSON; sets `Content-Type: application/json` |
| `mode` | `str` | Fetch mode: `"cors"`, `"no-cors"`, `"same-origin"` |
| `credentials` | `str` | Cookie policy: `"omit"`, `"same-origin"`, `"include"` |
| `cache` | `str` | Cache mode: `"default"`, `"no-store"`, `"no-cache"`, … |
| `signal` | `JsProxy` | JS `AbortSignal` to cancel the request |

`json` and `body` are mutually exclusive.

---

## `HttpResponse`

The object returned by every request function.

### Properties

| Property | Type | Description |
| -------- | ---- | ----------- |
| `.ok` | `bool` | `True` if status is 200–299 |
| `.status` | `int` | HTTP status code (e.g. `200`, `404`) |
| `.status_text` | `str` | Status reason phrase (e.g. `"OK"`, `"Not Found"`) |

### Body methods (all async)

| Method | Returns | Description |
| ------ | ------- | ----------- |
| `await resp.json()` | `dict \| list \| …` | Parse body as JSON → native Python object |
| `await resp.text()` | `str` | Body as a plain string |
| `await resp.blob()` | `JsProxy` | JS Blob (for images, files, downloads) |
| `await resp.array_buffer()` | `JsProxy` | JS ArrayBuffer (for binary data) |

Each body method can only be called once per response (browser limitation).

---

## Common patterns

### POST JSON, handle errors

```python
async def create_item(e):
    set_saving(True)
    try:
        resp = await post(
            "https://api.example.com/items",
            json={"name": name, "qty": qty},
        )
        if resp.ok:
            created = await resp.json()
            set_items(lambda lst: [*lst, created])
        else:
            body = await resp.text()
            set_error(f"Server error {resp.status}: {body}")
    except Exception as exc:
        set_error(f"Network error: {exc}")
    finally:
        set_saving(False)
```

### Authenticated request

```python
TOKEN = "my-secret-token"

async def load_profile(e):
    resp = await get(
        "https://api.example.com/me",
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    if resp.ok:
        set_profile(await resp.json())
```

### Cancel a request with AbortSignal

```python
from js import AbortController

controller = None

async def start_fetch(e):
    global controller
    controller = AbortController.new()
    try:
        resp = await get(url, signal=controller.signal)
        set_data(await resp.json())
    except Exception:
        pass   # AbortError is raised on cancellation

def cancel(e):
    if controller:
        controller.abort()
```

### Load data on button click (with loading state)

```python
@component
def Posts():
    posts,   set_posts   = use_state([])
    loading, set_loading = use_state(False)

    async def load(e):
        set_loading(True)
        try:
            resp = await get("https://jsonplaceholder.typicode.com/posts?_limit=10")
            if resp.ok:
                set_posts(await resp.json())
        finally:
            set_loading(False)

    return div(
        button("Load posts", onClick=load, disabled=loading),
        p("Loading…") if loading else None,
        *[
            div(
                h3(post["title"]),
                p(post["body"]),
                style={"borderBottom": "1px solid #eee", "padding": "8px 0"},
            )
            for post in posts
        ],
    )
```

---

## CORS

All requests go through `window.fetch` and are subject to the same-origin policy.
Requests to a different domain require the server to return appropriate CORS headers:

```
Access-Control-Allow-Origin: *
```

Public APIs (JSONPlaceholder, OpenWeatherMap, GitHub, etc.) typically have CORS
enabled. If you control the backend, add CORS headers for your Gluon app's origin.
If you don't, use a serverless proxy function.

---

## Why `resp.json()` uses `json.loads` internally

The browser's `Response.json()` method returns a JavaScript Promise that resolves
to a native JS object. In Pyodide, JS objects arrive as `JsProxy` instances —
opaque wrappers that do not have Python dict methods like `.get()`, `.items()`,
or `["key"]` subscripting.

Gluon's `resp.json()` works around this by reading the body as text and parsing
it with Python's standard `json.loads`. The result is always a genuine Python
`dict` or `list` that behaves exactly as expected.

```python
data = await resp.json()
name = data["name"]          # works
name = data.get("name", "")  # works
for key, val in data.items(): # works
    ...
```

Never replace the implementation with `await self._js_response.json()` — that
returns JsProxy objects and breaks all dict access.
