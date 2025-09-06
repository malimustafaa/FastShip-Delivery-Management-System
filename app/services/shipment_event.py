from random import randint
from websockets import StatusLike
from app.database.models import ShipmentStatus
from app.database.models import Shipment, ShipmentEvent
from app.database.redis import add_shipment_verification_code
from app.services.base import BaseService
from app.services.notification import NotificationService
from app.config import app_settings
from app.worker.tasks import send_email_template, send_sms
from utils import generate_url_safe_token


class ShipmentEventService(BaseService):
    def __init__(self,session):
        super().__init__(session,ShipmentEvent)
       # self.notification_service= NotificationService(tasks) no longer used coz now we use Celery for background tasks (worker), not baground task itself

    async def add(self,shipment:Shipment,location:int = None,status:ShipmentStatus = None,description:str= None)->ShipmentEvent:
        last_event = await self.get_latest_event(shipment)
        if not location:
         if last_event:
            location = last_event.location
         else:
            raise ValueError("Location is required for the first event")
        if not status:
         if last_event:
            status = last_event.status
         else:
            raise ValueError("Status is required for the first event")

        new_event = ShipmentEvent(
            location = location,
            status=status,
            description=description if description else await self._generate_description(status,location),
            shipment_id = shipment.id,

        )
        await self._notify(shipment=shipment,status=status)
        return await self._create(new_event)
    
    async def get_latest_event(self,shipment:Shipment):
        if not shipment.timeline:
         return None
        timeline = shipment.timeline
        timeline.sort(key=lambda item: item.created_at)
        return shipment.timeline[-1] #will sort list from oldest to newest, and return most recent one
    
    async def _generate_description(self, status:ShipmentStatus, location:int):
        match status:
            case ShipmentStatus.placed:
                return "assign delivery partner"
            case ShipmentStatus.new:
                return "assign delivery partner"
            case ShipmentStatus.out_for_delivery:
                return "Order is on its way!"
            case ShipmentStatus.in_transit:
                return "Order is in transit mode!"
            case ShipmentStatus.cancelled:
              return "Order cancelled"
            case _: #default case
                return f"scanned at {location}"
    async def _notify(self,shipment:Shipment,status:ShipmentStatus):
      

       match status:
          case ShipmentStatus.placed:
              send_email_template.delay(
                recipients=[shipment.client_contact_email],
                subject= "Your order is shipped!",
                context = {
                   "id":shipment.id,
                   "seller":shipment.seller.name,
                   "partner":shipment.delivery_partner.name

                },
                template_name="mail_placed.html"
             )
          case ShipmentStatus.out_for_delivery:
             code = randint(100_000,999_999) #generating code to send using twilio
             await add_shipment_verification_code(shipment.id,code)
             if shipment.client_contact_phone:
                send_sms.delay(shipment.client_contact_phone,f"Your order is out for delivery! Share the code {code} with delivery rider to recieve your parcel.") #sending code on moble if number given
             send_email_template.delay(
                recipients=[shipment.client_contact_email],
                subject= "Your order is out for delivery!",
                context = {
                   "id":shipment.id,
                   "seller":shipment.seller.name,
                   "partner":shipment.delivery_partner.name,
                   "verification_code":code

                },
                template_name="mail_out_for_delivery.html"
            )
           
            
          case ShipmentStatus.in_transit:
              send_email_template.delay(
                recipients=[shipment.client_contact_email],
                subject= "Your order is in transit mode!",
                context = {
                   "id":shipment.id,
                   "seller":shipment.seller.name,
                   "partner":shipment.delivery_partner.name

                },
                template_name="mail_in_transit.html"
             )
          case ShipmentStatus.delivered:
             token = generate_url_safe_token({"id":str(shipment.id)})
             print(token)
             send_email_template.delay(
                recipients=[shipment.client_contact_email],
                subject= "Your order is delivered!",
                context = {
                   "id":shipment.id,
                   "seller":shipment.seller.name,
                   "partner":shipment.delivery_partner.name,
                   "review_url":f"http://{app_settings.APP_DOMAIN}/shipment/review?token={token}"


                },
                template_name="mail_delivered.html"
             )
             
          case ShipmentStatus.cancelled:
              send_email_template.delay(
                recipients=[shipment.client_contact_email],
                subject= "Your order is cancelled!",
                context = {
                   "id":shipment.id,
                   "seller":shipment.seller.name,
                   "partner":shipment.delivery_partner.name

                },
                template_name="mail_cancelled.html"
             )
          case ShipmentStatus.new:
              send_email_template.delay(
                recipients=[shipment.client_contact_email],
                subject= "Your order is shipped!",
                context = {
                   "id":shipment.id,
                   "seller":shipment.seller.name,
                   "partner":shipment.delivery_partner.name

                },
                template_name="mail_new.html"
             )
            
             
            
             
            




    


