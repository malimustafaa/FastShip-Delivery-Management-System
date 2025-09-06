from pydantic import BaseModel,Field#for pydantic models import from pydantic library
from typing import Optional
from enum import Enum
from datetime import datetime
from pydantic import EmailStr

class DeliveryPartnerBase(BaseModel):
    name:str 
    email:EmailStr 
    serviceable_zip_codes:list[int]
    max_handling_capacity:int
class DeliveryPartnerRead(DeliveryPartnerBase):
    pass
class DeliveryPartnerCreate(DeliveryPartnerBase):
    password:str
class DeliveryPartnerUpdate(BaseModel):
    serviceable_zipcodes:list[int]
    max_handling_capacity:int
    
