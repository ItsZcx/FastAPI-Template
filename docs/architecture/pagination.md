# Pagination

List endpoints in this template use **cursor (keyset) pagination** so responses stay fast and bounded even as tables grow. The reusable pieces live in `src/pagination.py`.

> 💡 *Cursor* (opaque "page token") pagination is preferable to plain `?page=` for large/changing datasets because the window is keyed off the last seen item rather than an offset that can drift or double-skip.

## 📦 What `src/pagination.py` exports

| Name                                           | Kind                   | Purpose                                                                       |
| ---------------------------------------------- | ---------------------- | ----------------------------------------------------------------------------- |
| `Page[T]`                                      | generic pydantic model | JSON envelope: `{ items: T[], next_cursor }`                                  |
| `encode_cursor(value)`                         | function               | turn a value (e.g. last id) into an opaque token                              |
| `decode_cursor(token)`                         | function               | revert a token; `None` in ⇒ `None` out (or start from beginning if malformed) |
| `apply_cursor(query, order_by, cursor, limit)` | function               | keyset query + returns `(items, next_cursor)`                                 |

Cursors are URL-safe base64 of a small JSON payload — they are **opaque** to clients, which only echo them back.

## 🧮 The cursor shape

The `Page[T]` model is the wire contract for every paginated list.

```json
{
  "items": [ {  "id": 1, "title": "Todo A",  ... } ],
  "next_cursor": "Mg=="
}
```

* When `next_cursor` is `null`, you reached the last page.
* `items` is always the requested page (never a slice leak of the fetched lookahead).

## 🔭 How a list endpoint uses it

The `todos` list endpoint is the runnable reference (`src/package/router.py`):

```python
from fastapi import Query
from src.pagination import Page, apply_cursor

@router.get("", status_code=status.HTTP_200_OK, response_model=Page[TodoRead])
def get_items(
    db: db_dependency,
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
):
    items, next_cursor = apply_cursor(db.query(Todos), Todos.id, cursor, limit)
    return Page[TodoRead](items=items, next_cursor=next_cursor)
```

Rules this endpoint encodes:

* `limit` has `ge=1, le=100` so a client can't request unbounded pages.
* The query is ordered by the cursor field (`Todos.id`); `apply_cursor`:
  1. orders by that field
  2. filters `field > decoded_cursor` when a cursor is supplied
  3. fetches `limit + 1` rows to detect whether a further page exists
  4. returns exactly `limit` items + the next cursor (or `None` if there is no more)

## 👣 Calling it

```bash
# page 1
curl 'http://localhost:8080/todos?limit=2'
# => { "items": [ ...2 rows... ], "next_cursor": "Mg==" }

# follow the cursor for page 2
curl 'http://localhost:8080/todos?limit=2&cursor=Mg=='
# => { "items": [ ...1 row... ], "next_cursor": null }
```

## ⚠️ Design notes & extensions

* **Single-field cursor**: `apply_cursor` is implemented for one ordered field (commonly the primary key `id`). This is usually enough — records rarely need a true multi-column sort key.
* **Ascending order**: implemented for monotonically increasing keys. To reverse order, negate the comparison (`field < last`) or extend `apply_cursor` to take a direction.
* **Envelope reuse**: because `Page` is generic you can produce `Page[TodoRead]`, `Page[UserRead]`, etc. FastAPI resolves the parametrized generic into clean OpenAPI schemas automatically.
* **Total count**: not included on purpose (counting defeats keyset's purpose on huge tables). If a client needs totals, add an explicit `/count` endpoint instead.

## 🧪 Testing pagination

Two tests in `tests/package/test_todos.py` create 3 rows then assert page 1 returns 2 items + a cursor and page 2 returns 1 item + `null` cursor — run them with the rest of the suite (see [Testing](testing.md)).
