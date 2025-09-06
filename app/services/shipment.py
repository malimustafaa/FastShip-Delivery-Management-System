from email.policy import HTTP
from turtle import st
from fastapi import HTTPException,status
from app.core.exceptions import ClientNotAuthorized, EntityNotFound, InvalidToken, NoTokenData, TagDoesNotExist, VerificationCodeRequired
from app.database.models import DeliveryPartner, Review, Shipment,Seller, TagName
from app.api.schemas.shipment import ShipmentCreate, ShipmentReview,ShipmentStatus, UpdateShipment
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime,timedelta
from uuid import UUID
from app.database.redis import get_shipment_verification_code
from app.services.base import BaseService
from app.services.shipment_event import ShipmentEventService
from utils import decode_url_safe_token
from .delivery_partner import DeliveryPartnerService
from sqlalchemy.orm import selectinload



class ShipmentService(BaseService):
    def __init__(self,session:AsyncSession,partner_service:DeliveryPartnerService,event_service:ShipmentEventService):
       
       super().__init__(session,Shipment)
       self.partner_service = partner_service
       self.event_service = event_service

    async def get(self,id:UUID)-> Shipment:
     shipment = await self._get(id)
     if not shipment:
        raise EntityNotFound()
     return shipment
    
    async def add(self,body:ShipmentCreate,seller:Seller):

        new_shipment = Shipment(
        **body.model_dump(),
        status = ShipmentStatus.placed,
        estimated_delivery=datetime.now() + timedelta(days=3), #estimated delivery by default is 3 days
        seller_id = seller.id
    )
        partner = await self.partner_service.assign_shipment(new_shipment)
        if partner:
           new_shipment.delivery_partner_id = partner.id
           new_shipment.delivery_partner = partner
        

        shipment = await self._create(new_shipment)
        event = await self.event_service.add(
           shipment=shipment,
           location = seller.zip_code,
           status = ShipmentStatus.placed,
           description = f"assigned to {partner.name}"
        )
        shipment.timeline.append(event)

        return shipment
    
    async def get_field(self,field:str,id:UUID):
     shipment = await self.session.get(Shipment,id)
     value = getattr(shipment,field,None)#to get specifc field value
     return { field: value}

    async def update(self,id:UUID,shipment_update:UpdateShipment,partner:DeliveryPartner):
         shipment = await self.get(id)
         if not shipment:
            raise EntityNotFound()
         if shipment.delivery_partner_id != partner.id:
            raise ClientNotAuthorized()
         if shipment_update.status == ShipmentStatus.delivered:
            if not shipment_update.verification_code:
             raise VerificationCodeRequired()
            code = await get_shipment_verification_code(shipment.id)
            if str(code) != str(shipment_update.verification_code):
               print("code",code)
               print("verification_code",shipment_update.verification_code)
               raise ClientNotAuthorized()
            
            
         update = shipment_update.model_dump(exclude_none=True,exclude=["verification_code"])
         if shipment_update.estimated_delivery:
            shipment.estimated_delivery = shipment_update.estimated_delivery
         if len(update)>1 or not shipment_update.estimated_delivery:  #if any other thing to be updated except for estimated_elivery
            await self.event_service.add(
               shipment=shipment,
               **update
         ) 
         return await self._update(shipment)
    
    async def cancel(self,id,seller:Seller):
       #validate the seller
       shipment = await self.get(id)
       if shipment.seller_id != seller.id:
          raise ClientNotAuthorized()
       event = await self.event_service.add(
           shipment=shipment,
           status=ShipmentStatus.cancelled

        )
       shipment.timeline.append(event)
       shipment = await self._update(shipment)
       return shipment
    
   


    async def delete(self,id:UUID):
       shipment = await self._get(id)
       self._delete(shipment)
       return "Deletion Done"
    

    async def rate(self,token:str,rating:int,comment:str):
       token_data = decode_url_safe_token(token)
       print(token_data)
       if not token_data:
          raise InvalidToken()
       shipment = await self.get(UUID(token_data["id"]))
       new_review = Review(
          rating = rating,
          comment = comment if comment else None,
          shipment_id = shipment.id,
       )
       self.session.add(new_review)
       await self.session.commit()

   
    async def add_tag(self,id:UUID,tag_name:TagName):
       shipment = await self.get(id)
       tag_i= await tag_name.tag(self.session)
       print("tag is: ",tag_i)
       shipment.tags.append(tag_i)
       return await self._update(shipment)
       
    async def remove_tag(self,id:UUID,tag_name:TagName):
       shipment = await self.get(id)
       try:
          shipment.tags.remove(await tag_name.tag(self.session))
       except ValueError:
          raise TagDoesNotExist()
       return await self._update(shipment)
       

       





