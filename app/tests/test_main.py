
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_app(client:AsyncClient):
    response = await client.get("/") #to check if server is running , defined in main.py read_post, "/" is the url
    print(f"[Response]: {response.json()}")
    assert response.status_code == 200
