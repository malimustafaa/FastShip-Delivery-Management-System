from app.core.exceptions import NoRelevantPartnerFound, PartnerNotFound
from app.database.models import DeliveryPartner,Shipment
from .user import UserService
from app.api.schemas.delivery_partner import DeliveryPartnerCreate
from uuid import UUID
from sqlmodel import select,any_
from typing import Sequence
from fastapi import BackgroundTasks, HTTPException,status

class DeliveryPartnerService(UserService):
    def __init__(self,session):
        super().__init__(DeliveryPartner,session)
    
    async def add(self,delivery_partner:DeliveryPartnerCreate):
        return await self._add_user(delivery_partner.model_dump(),"partner")
    
    async def get(self,id:UUID):
     partner = await self._get(id)
     return partner
    
    async def token(self,email,password):
        return await self._generate_token(email,password)
    
    async def update(self,id:UUID,body:dict):
        partner = await self.session.get(DeliveryPartner,id)
        partner.sqlmodel_update(body)
        return await self._update(partner)
    
    async def get_partners_by_zipcode(self,zipcode:int) -> Sequence[DeliveryPartner]:
        result = await self.session.scalars(
             select(DeliveryPartner).where(zipcode == any_( DeliveryPartner.serviceable_zip_codes))
        )
        return result.all()
    async def assign_shipment(self,shipment:Shipment):
        eligible_partners = await self.get_partners_by_zipcode(shipment.destination)
        for partner in eligible_partners:
            if partner.current_handling_capacity > 0:
                partner.shipments.append(shipment)
                return partner
        raise NoRelevantPartnerFound()
            

