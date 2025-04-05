"""Test root endpoint."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root(client: AsyncClient) -> None:
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "docs" in response.json()
    assert "redoc" in response.json()
