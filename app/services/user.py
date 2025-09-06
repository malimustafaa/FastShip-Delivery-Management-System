from datetime import timedelta
from uuid import UUID
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EmailNotVerified, EntityNotFound, IncorrectPassword, InvalidToken, NoTokenData
from app.database.models import User
from app.services.notification import NotificationService
from app.worker.tasks import send_email_template
from .base import BaseService
from sqlalchemy import select
from passlib.context import CryptContext
from utils import decode_url_safe_token, generate_access_token, generate_url_safe_token
from fastapi import BackgroundTasks, HTTPException,status
from ..config import app_settings


password_context = CryptContext(schemes=['bcrypt'])
class UserService(BaseService):
    def __init__(self,model:User,session:AsyncSession):

        self.model = model
        self.session = session
        #self.notification_service = NotificationService(tasks)
    
    async def _get_by_email(self,email)-> User | None:
        return await self.session.scalar(
            select(self.model).where(self.model.email == email)
        )
    async def _generate_token(self,email,password):
         #validate the credentials
        #we not using get methos here, because get only works with primary key
         #so we use select here
        result = await self._get_by_email(email)
         #returns seller object with that email, .scalars().all() will return list of all seller objects with same email
        if result is None:
            raise EntityNotFound()
        if not password_context.verify(password,result.password_hash):
            raise IncorrectPassword()
        if not result.email_verified:
            raise EmailNotVerified()
        

        token = generate_access_token(
            data= {
                "user": result.name,
                "id": str(result.id)
            }
        )
        return token
    
    async def _add_user(self,data:dict,router_prefix:str):
        user = self.model(
            **data,
            password_hash = password_context.hash(data["password"]))
        user1 = await self._create(user)
        token = generate_url_safe_token({
            #"email":user1.email,
            "id": str(user1.id)
        }  )
        send_email_template.delay(
            recipients = [user1.email],
            subject="Verify Your Account With Fastship",
            context = {
                "username":user1.name,
                "verification_url":f"http://{app_settings.APP_DOMAIN}/{router_prefix}/verify?token={token}"

            },
            template_name = "mail_email_verify.html"
        )

        return user
    
    async def verify_email(self,token:str):
        token_data = decode_url_safe_token(token)
        if not token_data:
            raise InvalidToken()
        user = await self._get(UUID(token_data["id"]))
        user.email_verified = True
        await self._update(user)

    async def send_password_reset_link(self,email:EmailStr,router_prefix:str):
        user = await self._get_by_email(email)
        token = generate_url_safe_token({"id":str(user.id)},salt="password-reset")
        send_email_template.delay(
            recipients=[user.email],
            subject = "Fastship Account Password Reset",
            context = {
                "username":user.name,
                "reset_url":f"http://{app_settings.APP_DOMAIN}/{router_prefix}/reset_password_form?token={token}"

            },template_name="mail_password_reset.html"

        )
    async def reset_password(self,token:str,password:str)->bool:
        token_data = decode_url_safe_token(
            token,salt='password-reset',
            expiry = timedelta(days=1)
        )
        print("Decoded token:", token_data)
        print("User id from token:", token_data['id'])

        if not token_data:
            return False
        user = await self._get(UUID(token_data["id"]))
        user.password_hash = password_context.hash(password)
        await self._update(user)
        return True

        



    




    
    