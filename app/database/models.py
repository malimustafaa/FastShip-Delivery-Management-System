from sqlmodel import SQLModel,Field,Relationship #for sql(orm) model import from sqlmodel library
from enum import Enum
from datetime import datetime
from pydantic import EmailStr
from uuid import UUID,uuid4
from sqlalchemy import Boolean, Column,ARRAY,INTEGER,func, select, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession

class ShipmentStatus(str,Enum): #str indicates all values will be of str, and no other value shall be accepted
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    new = "new"
    delivered = "delivered"
    cancelled = "cancelled"

class TagName(str,Enum):
    EXPRESS = "EXPRESS"
    STANDARD = "STANDARD"
    FRAGILE = "FRAGILE"
    HEAVY = "HEAVY"
    INTERNATIONAL = "INTERNATIONAL"
    DOMESTIC = "DOMESTIC"
    TEMPERATURE_CONTROLLED = "TEMPERATURE_CONTROLLED"
    GIFT = "GIFT"
    RETURN = "RETURN"
    DOCUMENTS = "DOCUMENTS"

    async def tag(self,session:AsyncSession):
        return await session.scalar(
            select(Tag).where(Tag.name == self)
        )
    '''

    Use self when your DB column is stored as an ENUM type (our case, name is type TagName directly, so we dont need .value to compare,we can copare directly).
    Tag.name is of type TagName (Postgres enum).
    self is also TagName.EXPRESS (enum object).

Use self.value when your DB column is stored as a string (TEXT or VARCHAR).
    eg:
    tag = await TagName.EXPRESS.tag(session)
    here self == EXPRESS or GIFT etc object, value = "express' , 'gift'

# SQL behind the scenes:
# SELECT * FROM tag WHERE tag.name = 'express';

    '''

#Link Table -> for many to many  (shipment and tag), must define above both involved table, in our case shipments and tags

class ShipmentTag(SQLModel,table=True):
    __tablename__ = "shipment_tag"
    shipment_id:UUID = Field(
        foreign_key="shipment.id",
        primary_key = True #combination of shipment_id and tag_id as foreign key 
    )
    tag_id:UUID = Field(
        foreign_key="tag.id",
        primary_key=True
        )
    

class Shipment(SQLModel,table=True): #table=True to create table of this class in database, else it will work as pydntic model
    __tablename__ = "shipment"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content:str
    weight:float = Field(le=25)
    destination:int = Field(
        description=" location zipcode"
    )
    status:ShipmentStatus
    estimated_delivery: datetime
    seller_id:UUID = Field(foreign_key="seller.id")
    delivery_partner_id:UUID = Field(foreign_key="delivery_partner.id")
    delivery_partner:"DeliveryPartner"=Relationship(back_populates=("shipments"),sa_relationship_kwargs={"lazy":"selectin"})
    seller: "Seller" = Relationship(back_populates=("shipment"), sa_relationship_kwargs={"lazy":"selectin"})
    created_at:datetime= Field(sa_column=Column(
        postgresql.TIMESTAMP,
        default=func.now(),
        nullable=False
    ))
    client_contact_email: EmailStr 
    client_contact_phone:str | None
    timeline: list["ShipmentEvent"] = Relationship(back_populates="shipment",sa_relationship_kwargs={"lazy":"selectin"})
    review:"Review" = Relationship(back_populates="shipment",sa_relationship_kwargs={"lazy":"selectin"})
    tags: list["Tag"] = Relationship(back_populates="shipments",link_model=ShipmentTag,sa_relationship_kwargs={"lazy":"immediate"})
#lazy:immediate coz else it will give error when queried coz of link model ig, so both tables are given immediate 
    @property
    def status(self):
        return self.timeline[-1].status if len(self.timeline) > 0 else None
#back populates mean if change in one table then that will reflect in that tables instance in other table as well, to keep both tables uptodate and avoid data disbalance



class User(SQLModel):
    name:str
    email:EmailStr
    password_hash :str
    email_verified: bool = Field(default=False)

class Seller(User,table=True):
    __tablename__ = "seller"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    shipment : list[Shipment] = Relationship(back_populates=("seller"),
                                             sa_relationship_kwargs={"lazy":"selectin"}) 
    
    created_at:datetime= Field(sa_column=Column(
        postgresql.TIMESTAMP,
      default=func.now(),
        nullable=False
    ))
    address:str | None = Field(default=None)
    zip_code:int | None = Field(default=None)
    
    
    '''
    sa_relation_kwargs: It avoids huge joins

Loads data efficiently
    '''
class DeliveryPartner(User,table=True):
    __tablename__ = "delivery_partner"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    serviceable_zip_codes: list[int] = Field(
        sa_column=Column(ARRAY(INTEGER))
     
    )
    max_handling_capacity:int
    shipments:list[Shipment] = Relationship(back_populates=("delivery_partner"),sa_relationship_kwargs={"lazy":"selectin"})
    created_at:datetime= Field(sa_column=Column(
        postgresql.TIMESTAMP,
       default=func.now(),
        nullable=False
    ))
    
    @property #make function callabe without paranthesis "()"
    def active_shipments(self):
        return [
            shipment for shipment in self.shipments if shipment.status != ShipmentStatus.delivered or shipment.status != ShipmentStatus.cancelled
        ]
    @property
    def current_handling_capacity(self):
       return self.max_handling_capacity - len(self.active_shipments)
    
class ShipmentEvent(SQLModel,table=True):
    __tablename__ = "shipment_event"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    
    created_at:datetime= Field(sa_column=Column(
        postgresql.TIMESTAMP,
      default=func.now(),
        nullable=False
    ))
    location:int
    status:ShipmentStatus
    description:str | None = Field(default=None)
    shipment_id :UUID = Field(foreign_key="shipment.id")
    shipment:Shipment = Relationship(back_populates="timeline",sa_relationship_kwargs={"lazy":"selectin"})

class Review(SQLModel,table=True):
    __tablename__ = "review"
    id:UUID = Field(default_factory=uuid4,primary_key=True)
    created_at:datetime = Field(sa_column=Column(
        postgresql.TIMESTAMP,
        default=func.now(),
        nullable=False


    ))
    rating:int = Field(ge=1,le=5)
    comment:str | None = Field(default=None)
    shipment_id:UUID = Field(foreign_key="shipment.id") #name of table dot name of column
    shipment:Shipment = Relationship(back_populates="review",sa_relationship_kwargs={"lazy":"selectin"})




    


# tagging a shipment (express,fragile etc)
class Tag(SQLModel,table=True):
    __tablename__ = "tag"
    id:UUID = Field(default_factory=uuid4,primary_key=True)
    name:TagName
    instruction:str
    shipments:list[Shipment] = Relationship(back_populates="tags",link_model = ShipmentTag,sa_relationship_kwargs={"lazy":"immediate"})
    











    

