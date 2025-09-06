from sqlmodel import SQLModel
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from app.config import db_settings
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
     db_settings.postgres_url(),
    echo = True,
    
)
 
async def create_db_tables():
  async with engine.begin() as connection:
    from .models import Shipment,Seller
    await connection.run_sync(SQLModel.metadata.create_all)
    


async def get_session():
 async_session = sessionmaker(
   bind=engine,
   class_=AsyncSession,
   expire_on_commit = False,
 )
 async with async_session() as session:
  yield session


SessionDep = Annotated[AsyncSession,Depends(get_session)]

