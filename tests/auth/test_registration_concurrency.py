import time
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.orm import Session

from src.auth.exceptions import UserAlreadyExists
from src.auth.schemas import UserCreate
from src.auth.service import create_user


def _attempt(connection, email, username):
    """Register one user on its own session/connection and report the outcome."""
    session = Session(bind=connection, expire_on_commit=False)
    try:
        create_user(session, UserCreate(email=email, username=username, password="123456789"))
        return "created"
    except UserAlreadyExists as error:
        return f"conflict-{error.field}"
    finally:
        session.close()


def test_concurrent_register_never_crashes(engine):
    """
    The DB unique constraints (not just the service's pre-checks) are the last
    line of defence. When several signups for the same email run at once, exactly
    one must succeed and the rest must become UserAlreadyExists (HTTP 409) - never
    an uncaught IntegrityError propagated as a 500.
    """
    email = f"race-{int(time.time() * 1000)}@example.com"

    with ThreadPoolExecutor(max_workers=6) as pool:
        connections = [engine.connect() for _ in range(6)]
        try:
            futures = [pool.submit(_attempt, conn, email, f"racer{i}") for i, conn in enumerate(connections)]
            results = [f.result() for f in futures]
        finally:
            for conn in connections:
                conn.close()

    created = [r for r in results if r == "created"]
    conflicts = [r for r in results if r.startswith("conflict-")]
    unexpected = [r for r in results if not (r == "created" or r.startswith("conflict-"))]

    assert not unexpected, f"unhandled outcomes escaped as 500s: {unexpected}"
    assert len(created) == 1, f"expected exactly one winner, got {created}"
    assert len(conflicts) == 5, "the losing signups should map to clean 409 conflicts"
