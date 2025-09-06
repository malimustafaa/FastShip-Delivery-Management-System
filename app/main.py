from time import perf_counter
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from contextlib import asynccontextmanager

from app.core.exceptions import  add_exception_handlers
from app.worker.tasks import add_log
from .api.routers.shipment import router
from .api.router import master_router

from app.database.session import create_db_tables


description = """
Delivery Management System for sellers and delivery agents.

### Seller 
- submit shipment effortlessly
- share tracking links with customers 

### Delivery Agents
- Auto accept shipments
- Track and update shipment status
- Email and SMS notifications

"""

@asynccontextmanager
async def lifespan_handler(app:FastAPI):
    await create_db_tables()
    yield


app = FastAPI(lifespan=lifespan_handler,
              title = "FastShip",
              description= description,
              )

app.add_middleware( #to allow requests from different origins 
    CORSMiddleware,
    allow_origins = ["*"], #* means allow from every port, any origin,(public api) if we want only speciifc to have access, we can define http://localhost:5000
    allow_methods = ["*"] #all methods GET,POST,DELETE,PATCH allowed 
)

app.include_router(master_router)

add_exception_handlers(app) #for handling custom exception (exception.py)

@app.middleware("http")
async def custom_middleware(request:Request,call_next):
    start = perf_counter()

    response:Response = await call_next(request)
    end = perf_counter()
    time_taken = round(end-start,2)
    add_log.delay(f"{request.method} {request.url} {response.status_code} {time_taken}sec")
    return response

@app.get("/")
def read_post():
    return {"detail":"server is running..."}










@app.get('/scalar',include_in_schema=False) #for scalar ui
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title = "ScalarAPI",
    )








