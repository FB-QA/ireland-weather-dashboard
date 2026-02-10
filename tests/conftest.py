"""Shared test configuration and fixtures."""

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture
async def async_client():
    """Async HTTP client wired to the FastAPI app (no real server needed)."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
