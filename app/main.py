
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import ApplicationException
from app.api.router import api_router


setup_logging(settings.LOG_LEVEL)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s", settings.APP_NAME)
    print("backend URL is : http://127.0.0.1:8000")

    yield

    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Enable CORS for frontend running from file://, Live Server (port 5500, 3000, 8080), or localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ApplicationException)
async def application_exception_handler(
    request: Request,
    exc: ApplicationException
):
    logger.error("Application error: %s", exc.message)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message
        }
    )


app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX
)


@app.get("/", tags=["Root"])
async def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }
