# Router with the endpoints
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Path
from starlette import status

from src.database import db_dependency
from src.package.models import Todos
from src.package.schemas import TodoRequest

router = APIRouter(prefix="/todos", tags=["Todos"])


@router.get("", status_code=status.HTTP_200_OK)
def get_items(db: db_dependency):
    return db.query(Todos).all()


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
def get_item(db: db_dependency, todo_id: int = Path(gt=0)):
    model = db.query(Todos).filter(Todos.id == todo_id).first()

    if model is not None:
        return model
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("", status_code=status.HTTP_201_CREATED)
def post_item(db: db_dependency, todo_request: TodoRequest):
    model = Todos(**todo_request.model_dump())

    db.add(model)
    db.commit()


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def put_item(db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    model = db.query(Todos).filter(Todos.id == todo_id).first()

    if model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    model.title = todo_request.title
    model.description = todo_request.description
    model.complete = todo_request.complete

    db.add(model)
    db.commit()


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(db: db_dependency, todo_id: int = Path(gt=0)):
    model = db.query(Todos).filter(Todos.id == todo_id).first()

    if model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
