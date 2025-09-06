


from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from app.config import notification_settings
from utils import TEMPLATE_DIR
from twilio.rest import Client

class NotificationService:
    def __init__(self,tasks:BackgroundTasks):
        self.tasks = tasks #background task coz sending mail can be time consuming, using background task makes it quick
        self.fastmail = FastMail(
           ConnectionConfig(
           ** notification_settings.model_dump(exclude = ["TWILIO_SID",'TWILIO_AUTH_TOKEN',"TWILIO_NUMBER"]),
           TEMPLATE_FOLDER = TEMPLATE_DIR

    )
        )
        self.twilio_client = Client(
    username=notification_settings.TWILIO_SID,
    password=notification_settings.TWILIO_AUTH_TOKEN
)
    async def send_email(self,reciptents:list[EmailStr],subject:str,body:str):
        self.tasks.add_task(
            self.fastmail.send_message,
            message=MessageSchema(
            recipients=reciptents,subject=subject,body=body,subtype=MessageType.plain


        )
        )
    async def send_email_template(self,
                                  recipients:list[EmailStr],
                                  subject:str,
                                  context:dict,
                                  template_name:str ):
        self.tasks.add_task(self.fastmail.send_message,
                            message=MessageSchema(
            recipients=recipients,subject=subject,template_body=context,subtype=MessageType.html


        ),template_name = template_name
        )
        print(TEMPLATE_DIR)
    async def send_sms(self,to:str,body:str):
        await self.twilio_client.messages.create_async(
            from_=notification_settings.TWILIO_NUMBER,
            to = to,
            body=body
        )
        
        
