
from twilio.rest import Client
from app.config import notification_settings

#using client we can send msgs with twilio
'''client = Client(
    username=notification_settings.TWILIO_SID,
    password=notification_settings.TWILIO_AUTH_TOKEN
)

client.messages.create(
    from_=notification_settings.TWILIO_NUMBER,
    to="+13212472382",
    body=

)''''''













import asyncio
from fastapi_mail import ConnectionConfig, FastMail,MessageSchema, MessageType
from app.config import notification_settings

fastmail = FastMail(
    ConnectionConfig(
       ** notification_settings.model_dump()

    )
)
async def send_message():
    await fastmail.send_message(
        message = MessageSchema(
            recipients = ["shipment@xyz.com"],
            subject = "your email delivered with fastmail",
            body = "our first mail..",
            subtype = MessageType.plain, #type of msg, html or plaintext
        

        )
        
    )
    print("Email Sent!")
asyncio.run(send_message()) '''