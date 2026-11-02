from fastapi import Depends, Request
import httpx
from src.clients.fakestore_client import FakeStoreClient
from src.config import Settings, get_settings


def get_http_client(request: Request) -> httpx.AsyncClient:
    """
    Retrieve the shared httpx.AsyncClient instance from application state.
    Reuses connection pools and sockets across requests.
    """
    if hasattr(request.app.state, "http_client") and request.app.state.http_client is not None:
        return request.app.state.http_client
    # Fallback if accessed outside of normal lifespan lifecycle
    return httpx.AsyncClient()


def get_fakestore_client(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> FakeStoreClient:
    """
    FastAPI dependency that provides an initialized FakeStoreClient.
    """
    return FakeStoreClient(client=client)
