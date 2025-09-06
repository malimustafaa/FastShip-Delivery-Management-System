from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas.seller import SellerCreate
from app.database.models import Seller

from sqlalchemy import select
from fastapi import BackgroundTasks, HTTPException,status
from utils import generate_access_token
from app.services.base import BaseService
from passlib.context import CryptContext
from .user import UserService

password_context = CryptContext(schemes=['bcrypt'])

class SellerService(UserService):
    def __init__(self,session:AsyncSession):
        super().__init__(Seller,session)
    async def add(self,seller:SellerCreate):
       
        return  await self._add_user(seller.model_dump(),"seller")
       
    async def token(self,email,password)->str:
      return await self._generate_token(email,password)




    
