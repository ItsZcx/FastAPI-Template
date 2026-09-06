# Router with the endpoints
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Path
from fastapi import Query
from starlette import status

from src.core.database import db_dependency
from src.package.models import Todos
from src.package.schemas import TodoRead
from src.package.schemas import TodoRequest
from src.pagination import Page
from src.pagination import apply_cursor

router = APIRouter(prefix="/todos", tags=["Todos"])


@router.get("", status_code=status.HTTP_200_OK, response_model=Page[TodoRead])
def get_items(
    db: db_dependency,
    cursor: str | None = Query(default=None, description="Opaque cursor of the last item of the previous page."),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of todos to return per page."),
):
    """
    List todos using cursor pagination.

    Returns up to `limit` items plus a `next_cursor` to fetch the next page.
    Pass `next_cursor` back as the `cursor` query parameter until `next_cursor`
    is `null`.
    """
    items, next_cursor = apply_cursor(db.query(Todos), Todos.id, cursor, limit)
    return Page[TodoRead](items=items, next_cursor=next_cursor)


@router.get("/{todo_id}", status_code=status.HTTP_200_OK, response_model=TodoRead)
def get_item(
    db: db_dependency,
    todo_id: int = Path(gt=0, description="Id of the todo to fetch."),
):
    """
    Fetch a single todo by its id.

    Returns 404 if no todo with that id exists.
    """
    model = db.query(Todos).filter(Todos.id == todo_id).first()

    if model is not None:
        return model
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TodoRead)
def post_item(db: db_dependency, todo_request: TodoRequest):
    """
    Create a new todo.

    The created todo (including its `id`) is returned.
    """
    model = Todos(**todo_request.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def put_item(
    db: db_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0, description="Id of the todo to update."),
):
    """
    Replace a todo by its id.

    Returns 404 if no todo with that id exists.
    """
    model = db.query(Todos).filter(Todos.id == todo_id).first()

    if model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    model.title = todo_request.title
    model.description = todo_request.description
    model.complete = todo_request.complete

    db.add(model)
    db.commit()


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    db: db_dependency,
    todo_id: int = Path(gt=0, description="Id of the todo to delete."),
):
    """
    Delete a todo by its id.

    Returns 204 on success. Returns 404 if no todo with that id exists.
    """
    model = db.query(Todos).filter(Todos.id == todo_id).first()

    if model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
