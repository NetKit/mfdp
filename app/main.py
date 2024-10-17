from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.exceptions import HTTPException

from app.web.app import router as web_router
from app.repositories import repository_scope

from contextlib import asynccontextmanager

import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

current_dir = os.path.dirname(os.path.abspath(__file__))

static_dir = os.path.join(current_dir, "web/static")

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.include_router(web_router)

@app.exception_handler(HTTPException)
async def web_exception_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    if exc.status_code == 401:
        return RedirectResponse(url="/login")
    elif exc.status_code == 404:
        return RedirectResponse(url="/")
    else:
        return HTMLResponse(content="<h1>Something went wrong</h1>", status_code=exc.status_code)

@app.get("/liveness")
async def liveness():
    return {"status": "OK"}
