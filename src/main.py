from fastapi import FastAPI

from src.package.router import router as package_router

app = FastAPI(title="FastAPI-Template")
app.include_router(package_router)


@app.get("/")
def read_root():
    return {"msg": "Server is running"}
