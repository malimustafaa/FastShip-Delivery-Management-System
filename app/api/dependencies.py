from app.core.exceptions import EntityNotFound, InvalidToken, NoTokenData, PartnerNotFound, SellerNotFound, TokenDataExpired
from app.services.shipment import ShipmentService
from app.services.seller import SellerService
from app.services.delivery_partner import DeliveryPartnerService
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi import BackgroundTasks, Depends,HTTPException,status
from app.database.session import get_session
from app.core.security import oauth2_scheme_partner,oauth2_scheme_seller

from app.database.models import Seller,DeliveryPartner
from app.services.shipment_event import ShipmentEventService
from utils import decode_access_token
from app.database.redis  import is_jti_blacklisted
from uuid import UUID

SessionDep = Annotated[AsyncSession,Depends(get_session)]
def get_shipment_service(session:SessionDep,):
    return ShipmentService(session,DeliveryPartnerService(session),ShipmentEventService(session))

def get_seller_service(session:SessionDep):
    return SellerService(session)

def get_delivery_service(session:SessionDep):
    return DeliveryPartnerService(session)

#access token data dependency 
async def _get_access_token(token:str):

    data = decode_access_token(token=token)
    print("Decoded token data:", data) 
    
    if data is None:
        raise InvalidToken()

    if await is_jti_blacklisted(data["jti"]):
        raise TokenDataExpired()
   #there is "data":{ "user":12,"id":345}, so dictionary inside dict, we want "id" thats why data["data"] to get data dictioary inside outer data dict
    return data

async def get_seller_token(token:Annotated[str,Depends(oauth2_scheme_seller)]):
    return await _get_access_token(token)

async def get_partner_token(token:Annotated[str,(oauth2_scheme_partner)]):
    return await _get_access_token(token)





#logged in seller
async def get_current_seller(token_data:Annotated[dict,Depends(get_seller_token)],session:SessionDep):
     print("seller token triggered")
     seller =  await session.get(Seller,(UUID(token_data["data"]["id"])))
     if not seller: #to handle, valid token but user was deleted later after generting token case
        raise SellerNotFound()
     return seller

async def get_current_partner(token_data:Annotated[dict,Depends(get_partner_token)],session:SessionDep):
     print("partnr token triggered")
     partner =  await session.get(DeliveryPartner,(UUID(token_data["data"]["id"])))
     if not partner: #to handle, valid token but user was deleted later after generting token case
        raise PartnerNotFound()
     return partner

ActiveSellerDep = Annotated[Seller,Depends(get_current_seller)]
ActivePartnerDep = Annotated[DeliveryPartner,Depends(get_current_partner)]

ServiceDep = Annotated[ShipmentService,Depends(get_shipment_service)]
SellerDep = Annotated[SellerService,Depends(get_seller_service)]
DeliveryDep = Annotated[DeliveryPartnerService,Depends(get_delivery_service)]