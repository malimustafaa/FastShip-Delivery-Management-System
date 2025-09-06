from uuid import UUID
from jwt import decode
from redis.asyncio import Redis
from app.config import db_settings

# _ before token to make this variale private
_token_blacklist = Redis(
    host = db_settings.REDIS_HOST,
    port=db_settings.REDIS_PORT,
    db = 0
)
_shipment_verification_codes = Redis(
    host = db_settings.REDIS_HOST,
    port=db_settings.REDIS_PORT,
    db = 1,
    decode_responses=True
)
async def add_jti_to_blacklist(jti:str): #jti here is token id
   await _token_blacklist.set(jti,"blacklisted") #{jti:"blacklisted"}

async def is_jti_blacklisted(jti:str) -> bool:
   return await _token_blacklist.exists(jti)

async def add_shipment_verification_code(id:UUID,code:int):
  await _shipment_verification_codes.set(str(id),code) #{id:code}

async def get_shipment_verification_code(id:UUID):
   return await _shipment_verification_codes.get(str(id))


