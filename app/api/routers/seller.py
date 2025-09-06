from fastapi import APIRouter,Depends, Form,HTTPException, Request,status
from fastapi.templating import Jinja2Templates
from jinja2 import TemplateNotFound
from pydantic import EmailStr
from ..schemas.seller import SellerCreate,SellerRead
from app.services.seller import Seller, SellerService
from app.api.dependencies import SellerDep,SessionDep,get_seller_token
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from app.core.security import oauth2_scheme_seller
from utils import TEMPLATE_DIR, decode_access_token
from app.database.redis import add_jti_to_blacklist,is_jti_blacklisted
from app.config import app_settings

router = APIRouter(prefix='/seller',tags=['seller'])

@router.post("/signup",response_model=SellerRead)
async def register_seller(seller:SellerCreate,service:SellerDep):
   new_seller =  await service.add(seller)
   return new_seller

@router.post("/token")
async def login_seller(request_form:Annotated[OAuth2PasswordRequestForm,Depends()],service:SellerDep):
   token = await service.token(request_form.username,request_form.password)
   return {
      "token": token,
      "type":"jwt"
   }

##Verify seller email
@router.get("/verify")
async def verify_seller_email(token:str,service:SellerDep):
   await service.verify_email(token)
   return {"Account Verified!"}

# password reset link
@router.get("/forgot_password")
async def forogt_password(email:EmailStr,service:SellerDep):
   await service.send_password_reset_link(email,"seller")
   return {"Check email for password reset link! "}

#reset password form
@router.get('/reset_password_form')
async def reset_password_form(request:Request,token:str):
   templates=Jinja2Templates(directory=TEMPLATE_DIR)
   return templates.TemplateResponse(
      
      name="reset_password.html",
      context={
         "request":request,
         "reset_url":f"http://{app_settings.APP_DOMAIN}/seller/reset_password?token={token}",

      }
   )


# Reset seller password endpoint
@router.post("/reset_password") #Form here shws fastapi buildin format to extract parameter from html response, coz user sends new password from html form page 
async def reset_password(request:Request,token:str,password:Annotated[str,Form()],service:SellerDep):
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
      
@router.post('/logout')
async def logout_seller(token_data:Annotated[dict,Depends(get_seller_token)]):
   await add_jti_to_blacklist(token_data["jti"])
   return {
      "Successfully logged out!"
   }
