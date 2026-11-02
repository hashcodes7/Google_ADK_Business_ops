from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
import httpx
from src.config import Settings, get_settings
from src.routers.products import router as products_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager that runs once on startup and once on shutdown.
    Replaces deprecated @app.on_event handlers.
    Initializes shared async HTTP client session for FakeStoreAPI.
    """
    settings = get_settings()
    host_display = "localhost" if settings.HOST in ("0.0.0.0", "127.0.0.1") else settings.HOST
    print("=" * 64)
    print("  Multi-Agent Business Orchestration Platform Starting")
    print(f"  Environment       : {settings.APP_ENV.upper()}")
    print(f"  Uvicorn Host/Port : {settings.HOST}:{settings.PORT}")
    print(f"  Application URL   : http://{host_display}:{settings.PORT}")
    print(f"  API Docs (Swagger): http://{host_display}:{settings.PORT}/docs")
    print(f"  HTTP Timeout      : {settings.HTTP_TIMEOUT}s")
    print("=" * 64)

    # Initialize shared HTTP client with connection pooling
    app.state.http_client = httpx.AsyncClient(
        base_url=settings.ECOMMERCE_API_BASE_URL,
        timeout=settings.HTTP_TIMEOUT,
    )

    yield

    # Clean shutdown: close open connection pools and sockets
    print("Shutting down Multi-Agent Business Orchestration Platform cleanly...")
    if hasattr(app.state, "http_client") and app.state.http_client is not None:
        await app.state.http_client.aclose()


app = FastAPI(
    title="Multi-Agent Business Orchestration",
    description="Enterprise multi-agent orchestration platform integrating FakeStoreAPI.",
    version="0.1.0",
    lifespan=lifespan,
)

# Register API routers
app.include_router(products_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root(settings: Settings = Depends(get_settings)):
    """Health-check endpoint returning the active environment configuration."""
    return {
        "status": "ok",
        "environment": settings.APP_ENV,
        "ecommerce_api": settings.ECOMMERCE_API_BASE_URL,
    }


@app.get("/health", tags=["Health"])
async def health():
    """Liveness probe endpoint for Kubernetes / load balancers."""
    return {"status": "healthy"}
