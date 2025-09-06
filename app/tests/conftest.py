from fastapi.testclient import TestClient
import pytest
import pytest_asyncio
from app.main import app
from httpx import ASGITransport, AsyncClient

 #using this we can send request to any of our endpoints
@pytest_asyncio.fixture(scope="session") #with scope this function will run only once for the session instead of again again, and with fixture the result will be accessbile to all other functions 
async def client():
    async with AsyncClient(
        transport = ASGITransport(app), #making app async,
         base_url = 'http://test' #dummy url

    ) as client:
        yield client  #yield will pause it over here, then when test ends, it will execute the last line.

@pytest.fixture(scope="session",autouse=True) #autouse sets this to be runned every time
def setup_and_teardown():
    print("starting test...")
    yield
    print("finished!")

