import re
from typing import Annotated
from fastapi import APIRouter, Form, Query, Request
from fastapi import HTTPException,status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.exceptions import EntityNotFound, InvalidInput
from utils import TEMPLATE_DIR
from ..schemas.shipment import ShipmentCreate,ShipmentRead, ShipmentReview,UpdateShipment
from app.database.models import Shipment, TagName
from app.api.dependencies import SellerDep, ServiceDep,ActiveSellerDep,ActivePartnerDep, SessionDep
from uuid import UUID
from app.config import app_settings

router = APIRouter(prefix="/shipment",tags=["Shipment"])
templates = Jinja2Templates(TEMPLATE_DIR)

@router.get('/',response_model=ShipmentRead)
async def get_shipment(id:UUID ,service:ServiceDep,seller:ActiveSellerDep): #key type str, value type any
    shipment = await service.get(id)

    if  shipment is None:
        return EntityNotFound()
    return shipment
#Tracking details of shipment
@router.get('/track')
async def get_tracking(request:Request,id:UUID,service:ServiceDep):
    shipment = await service.get(id)
    context=shipment.model_dump()
    context["partner"] = shipment.delivery_partner.name
    context["status"] = shipment.status
    context["timeline"] = shipment.timeline
    context["timeline"].reverse() #from most recent status to old
    context["request"] = request
    return templates.TemplateResponse(
        #request=request,
        name="track.html",
        context=context

    )

@router.post('/',response_model=ShipmentRead,name="Create Shipment",description="submit a **shipment**")
async def submit_shipment(body:ShipmentCreate,service:ServiceDep,seller:ActiveSellerDep):
    new_shipment = await service.add(body,seller)
    return new_shipment

@router.get('/{field}')
async def get_shipment_field(field:str,id:UUID,service:ServiceDep,seller:ActiveSellerDep):
    shipment = await service.get(id)
    if shipment is None:
        raise EntityNotFound()
    shipment = await service.get_field(field,id)
    return shipment


@router.patch('/',response_model =  ShipmentRead) #for updating 'status' as the delivery process proceeds
async def patch_shipments(id:UUID,body:UpdateShipment,service:ServiceDep,partner:ActivePartnerDep): #Only active delivery partner wil be allowed to change status 
    update = body.model_dump(exclude_none=True) #remove data that has null value, if status given n date notor vice versa
    if not update: # if both vlaues not given, entirely null
         raise InvalidInput()
    shipment_update = await service.update(id,body,partner)
    return shipment_update



@router.get("/",response_model=ShipmentRead)
async def cancel_shipment(id:UUID,seller:ActiveSellerDep,service:ServiceDep):
    shipment = await service.get(id)
    return shipment

@router.post('/review')
async def submit_review_page(request:Request,token:str):
    print(token)
    return templates.TemplateResponse(request=request,name="review.html",context={"review_url":f"http://{app_settings.APP_DOMAIN}/shipment/submit_review?token={token}"})
    

@router.get('/submit_review')
async def submit_review(service:ServiceDep,rating:Annotated[int,Form(ge=1,le=5)],token:str = Query(...),comment:Annotated[str | None,Form()]=None):
    await service.rate(token,rating,comment)
    return {"detail":"Review submitted"}

#add a tag to shipment
@router.post('/tag',response_model =  ShipmentRead)
async def add_tag_to_shipment(id:UUID,tag_name:TagName,service:ServiceDep):
    return await service.add_tag(id,tag_name)

#remove a tag from shipment
@router.delete('/tag',response_model =  ShipmentRead)
async def remove_tag_from_shipment(id:UUID,tag_name:TagName,service:ServiceDep):
    return await service.remove_tag(id,tag_name)

#get all the shipments with the tag
@router.post("/tagged",response_model =  list[ShipmentRead])
async def get_shipments_with_tag(session:SessionDep,tag_name: TagName):
    tag = await tag_name.tag(session)
    return tag.shipments

# tag_name:TagName