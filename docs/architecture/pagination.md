# Pagination

List endpoints use cursor pagination, also called keyset pagination, so responses stay fast and bounded as tables grow. The reusable pieces live in `src/pagination.py`.

A cursor is preferable to `?page=` for large or changing datasets. The window keys off the last seen item, not an offset that can drift or double-skip.

## What `src/pagination.py` exports

| Name                                           | Kind                   | Purpose                                                                                     |
| ---------------------------------------------- | ---------------------- | ------------------------------------------------------------------------------------------- |
| `Page[T]`                                      | generic pydantic model | the JSON envelope `{ items: T[], next_cursor }`                                             |
| `encode_cursor(value)`                         | function               | turns a value, such as the last id, into an opaque token                                    |
| `decode_cursor(token)`                         | function               | turns the token back. `None` in gives `None` out, or start from the beginning if malformed. |
| `apply_cursor(query, order_by, cursor, limit)` | function               | runs the keyset query and returns `(items, next_cursor)`                                    |

Cursors are URL-safe base64 of a small JSON payload. Clients treat them as opaque and only echo them back.

## The cursor shape

`Page[T]` is the wire contract for every paginated list.

```json
{
  "items": [ {  "id": 1, "title": "Todo A",  ... } ],
  "next_cursor": "Mg=="
}
```

* A `null` `next_cursor` means you reached the last page.
* `items` holds exactly the requested page.

## How a list endpoint uses it

The `todos` list endpoint in `src/package/router.py` is the runnable reference:

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

`limit` uses `ge=1, le=100`, so a client cannot request unbounded pages.

`apply_cursor` orders the query by the cursor field, here `Todos.id`, then:

1. Filters `field > decoded_cursor` when a cursor is supplied.
2. Fetches `limit + 1` rows to detect whether a further page exists.
3. Returns exactly `limit` items and the next cursor, or `None` when there is no more.

## Call it

```bash
# page 1
curl 'http://localhost:8080/todos?limit=2'
# => { "items": [ ...2 rows... ], "next_cursor": "Mg==" }

# follow the cursor for page 2
curl 'http://localhost:8080/todos?limit=2&cursor=Mg=='
# => { "items": [ ...1 row... ], "next_cursor": null }
```

## Design notes and extensions

* **Single-field cursor.** `apply_cursor` keys off one ordered field, usually the primary key `id`. Records rarely need a multi-column sort key.
* **Ascending order.** It works for keys that increase. To reverse, compare `field < last`, or extend `apply_cursor` to take a direction.
* **Envelope reuse.** `Page` is generic, so you can return `Page[TodoRead]`, `Page[UserRead]`, and so on. FastAPI resolves the parametrized generic into OpenAPI schemas.
* **No total count.** Counting defeats keyset's purpose on large tables. If a client needs totals, add a `/count` endpoint.

## Test pagination

Two tests in `tests/package/test_todos.py` create three rows, then assert page 1 returns two items and a cursor, and page 2 returns one item and a `null` cursor. See [Testing](testing.md).
