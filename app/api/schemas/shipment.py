from pydantic import BaseModel, EmailStr,Field #for pydantic models import from pydantic library
from typing import Optional
from enum import Enum
from datetime import datetime
from uuid import UUID

from app.database.models import ShipmentEvent, Tag, TagName
from .seller import SellerRead
class BaseShipment(BaseModel):
    content:str = Field(max_length=100)
    destination: Optional[int] = None
    weight:float = Field(description="weight unit is in kg",lt=25,ge=1)


class ShipmentStatus(str,Enum): #str indicates all values will be of str, and no other value shall be accepted
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    new = "new"
    cancelled = "cancelled"
    delivered = "delivered"

class TagRead(BaseModel):
    name:TagName
    instruction:str

class ShipmentRead(BaseShipment):
    id: UUID
    timeline: list[ShipmentEvent]
    seller:SellerRead
    tags:list[TagRead]
 

class ShipmentCreate(BaseShipment):
    client_contact_email:EmailStr
    client_contact_phone:str | None = Field(default=None)

class UpdateShipment(BaseModel):
    status: ShipmentStatus | None = Field(default=None)
    estimated_delivery : datetime | None = Field(default=None)
    location:int | None = Field(default=None)
    description:str |None = Field(default=None)
    verification_code:int | None = Field(default=None)

class ShipmentReview(BaseModel):
    rating:int = Field(ge=1,le=5)
    comment:str|None = Field(default=None)

