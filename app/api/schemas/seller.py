from pydantic import BaseModel,Field#for pydantic models import from pydantic library
from typing import Optional
from enum import Enum
from datetime import datetime
from pydantic import EmailStr

class SellerBase(BaseModel):
    name:str 
    email:EmailStr 
class SellerRead(SellerBase):
    zip_code:int
class SellerCreate(SellerBase):
    password:str
    zip_code:int
    address:str

