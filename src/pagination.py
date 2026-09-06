# Global module: cursor-based pagination helpers and the generic Page model
import base64
import json
from typing import Generic
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Generic paginated response envelope."""

    items: list[T]
    next_cursor: str | None = None


def encode_cursor(value) -> str:
    """Encode an opaque cursor (e.g. the last item's sort key)."""
    payload = json.dumps(value, default=str)
    return base64.urlsafe_b64encode(payload.encode()).decode()


def decode_cursor(cursor: str | None):
    """Decode a cursor produced by encode_cursor. None in -> None out."""
    if cursor is None:
        return None
    try:
        payload = base64.urlsafe_b64decode(cursor.encode()).decode()
        return json.loads(payload)
    except Exception:
        # Treat malformed cursors as "start from the beginning"
        return None


def apply_cursor(query, order_by, cursor: str | None, limit: int):
    """
    Keyset pagination over a single monotonically increasing field (e.g. an integer id).

    Returns (items, next_cursor): `limit` items and the cursor for the next page,
    or None when there is no further page.
    """
    query = query.order_by(order_by)

    last_value = decode_cursor(cursor)
    if last_value is not None:
        query = query.filter(order_by > last_value)

    results = query.limit(limit + 1).all()

    has_more = len(results) > limit
    items = results[:limit]
    next_cursor = encode_cursor(getattr(items[-1], order_by.key)) if has_more and items else None

    return items, next_cursor
