from celery import Celery
from pydantic import EmailStr
from app.config import db_settings,notification_settings
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from asgiref.sync import async_to_sync #because celery doesnt support async functios, so we will convert to sycn
from twilio.rest import Client

from utils import TEMPLATE_DIR

fast_mail = FastMail(
           ConnectionConfig(
           **notification_settings.model_dump(exclude = ["TWILIO_SID",'TWILIO_AUTH_TOKEN',"TWILIO_NUMBER"]),
           TEMPLATE_FOLDER = TEMPLATE_DIR

    )
        )

send_message = async_to_sync(fast_mail.send_message) #sync version of send_message() function

app = Celery(
    "api_taks",
    broker = db_settings.REDIS_URL(9), #task queue from where salary will pick tasks and assign the worker
    backend = db_settings.REDIS_URL(9) #for storing return info from tasks

)
twilio_client = Client(
    username=notification_settings.TWILIO_SID,
    password=notification_settings.TWILIO_AUTH_TOKEN
)

@app.task #makes function celery task
def send_mail(
    #**kwargs
    
    recipients:list[str],
    subject:str,
    body:str
):
    #print(">>> kwargs:", kwargs)

    send_message(
        message = MessageSchema(recipients=recipients,subject=subject,body=body,subtype=MessageType.plain),
 
   )
    return "Message Sent! "

@app.task
def send_email_template(recipients:list[EmailStr], subject:str,context:dict,template_name:str ):
    send_message(message= MessageSchema(
            recipients=recipients,subject=subject,template_body=context,subtype=MessageType.html


        ),template_name = template_name
    )

@app.task
async def send_sms(to:str,body:str):
         twilio_client.messages.create_async(
            from_=notification_settings.TWILIO_NUMBER,
            to = to,
            body=body
        )
        
@app.task
def add_log(log:str):
      with open("file.log","a") as file:
            file.write(f"{log}\n")
            