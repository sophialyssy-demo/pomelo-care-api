import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import config
from .db import init_db
from .routers import auth, care_plans, care_team, documents, fhir, patients, providers

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Pomelo Care API", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth, patients, care_team, documents, fhir, providers, care_plans):
    app.include_router(r.router)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    body = {"detail": "Internal server error"}
    if config.DEBUG:
        body["error"] = repr(exc)
        body["trace"] = traceback.format_exc()
    return JSONResponse(status_code=500, content=body)


@app.get("/health")
def health():
    return {"status": "ok"}
