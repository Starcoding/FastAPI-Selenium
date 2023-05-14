from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from webdriver_manager.firefox import GeckoDriverManager

from app.logger import get_logger
from app.routers import (
    search,
)


app = FastAPI(
    title="TestCase",
    version="0.0.1",
    description="",
    swagger_ui_parameters={"persistAuthorization": False},
)

app.include_router(search.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
add_pagination(app)


@app.on_event("startup")
async def create_logs() -> None:
    get_logger(name="uvicorn.access", path="fast_api.log")


@app.on_event("startup")
def lock_workers():
    try:
        with open("lock_workers", "x") as file:
            file.write("lock workers")
    except FileExistsError:
        pass
