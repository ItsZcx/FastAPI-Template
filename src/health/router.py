# Liveness and readiness probes
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from src.core.database import db_dependency

router = APIRouter(tags=["Health"])


@router.get("/healthz", status_code=status.HTTP_200_OK)
def healthz():
    return {"status": "ok"}


@router.get("/readyz", status_code=status.HTTP_200_OK)
def readyz(db: db_dependency):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"status": "unavailable"})
    return {"status": "ready"}
