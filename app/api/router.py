from .routers import shipment,seller,delivery_partners
from fastapi import APIRouter

master_router  = APIRouter()
master_router.include_router(shipment.router)
master_router.include_router(seller.router)
master_router.include_router(delivery_partners.router)