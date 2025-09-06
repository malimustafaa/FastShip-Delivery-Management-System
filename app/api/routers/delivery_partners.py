from fastapi import APIRouter,Depends, Form,HTTPException, Request,status
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr

from app.core.exceptions import InvalidInput, PartnerNotFound
from ..schemas.delivery_partner import DeliveryPartnerCreate,DeliveryPartnerRead,DeliveryPartnerUpdate
from app.services.seller import Seller
from app.api.dependencies import SellerDep,SessionDep, get_partner_token,ActivePartnerDep,DeliveryDep
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from app.core.security import oauth2_scheme_partner
from utils import TEMPLATE_DIR, decode_access_token
from app.database.redis import add_jti_to_blacklist,is_jti_blacklisted
from app.config import app_settings

router = APIRouter(prefix='/partner',tags=['Delivery Partner'])

@router.post("/signup",response_model=DeliveryPartnerRead)
async def register_delivery_partner(partner:DeliveryPartnerCreate,service:DeliveryDep):
   new_partner =  await service.add(partner)
   return new_partner

@router.post("/token")
async def login_delivery_partner(request_form:Annotated[OAuth2PasswordRequestForm,Depends()],service:DeliveryDep):
   token = await service.token(request_form.username,request_form.password)
   return {
      "token": token,
      "type":"jwt"
   }

@router.post("/")
async def update_delivery_partner(body:DeliveryPartnerUpdate,partner:ActivePartnerDep,service:DeliveryDep):
    update = body.model_dump(exclude_none=True) #remove data that has null value, if status given n date notor vice versa
    if not update: # if both vlaues not given, entirely null
         raise InvalidInput()
    partner = await service.get(id)
    if partner is None:
         raise PartnerNotFound()
    partner_update = await service.update(id,update)
    return partner_update


@router.post('/logout')
async def logout_delivery_partner(token_data:Annotated[dict,Depends(get_partner_token)]):
   await add_jti_to_blacklist(token_data["jti"])
   return {
      "Successfully logged out!"
   }
@router.get("/verify")
async def verify_partner_email(token:str,service:DeliveryDep):
   await service.verify_email(token)
   return {"Account Verified!"}
@router.get("/forgot_password")
async def forogt_password(email:EmailStr,service:DeliveryDep):
   await service.send_password_reset_link(email,"partner")
   return {"Check email for password reset link! "}

#reset password form
@router.get('/reset_password_form')
async def reset_password_form(request:Request,token:str):
   templates=Jinja2Templates(directory=TEMPLATE_DIR)
   return templates.TemplateResponse(
      
      name="reset_password.html",
      context={
         "request":request,
         "reset_url":f"http://{app_settings.APP_DOMAIN}/partner/reset_password?token={token}",

      }
   )


@router.post("/reset_password") #Form here shws fastapi buildin format to extract parameter from html response, coz user sends new password from html form page 
async def reset_password(request:Request,token:str,password:Annotated[str,Form()],service:DeliveryDep):
   is_success = await service.reset_password(token,password)
   template = Jinja2Templates(TEMPLATE_DIR)
   if not is_success:
      return template.TemplateResponse(
      request= request,
      name= "password/password_reset_failed.html"
   )
   
   return template.TemplateResponse(
      request= request,
      name= "password/password_reset_successful.html"
   )




#for understanding it was, now activesellerdep doing itswork on shipment to only let logged in user to access functions and data, check dependencies
'''@router.get("/dashboard",response_model=SellerRead)
async def get_dashboard(token:Annotated[str,Depends(oauth2_scheme)],session:SessionDep):
   data =  decode_access_token(token=token)
   if data is None:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Access Token")
   seller = await session.get(Seller,data["data"]["id"])
   return seller'''
      