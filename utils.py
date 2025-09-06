from datetime import datetime,timedelta,timezone
from pathlib import Path
import jwt
from app.config import security_settings

from uuid import uuid4 #to assign unique id (random number) to each access token, to late add in blacklist at time of logout
from itsdangerous import BadSignature, Serializer, SignatureExpired, URLSafeSerializer, URLSafeTimedSerializer

_serializer = URLSafeTimedSerializer(security_settings.JWT_SECRET) #for email confirmation token, timed means after some time token will expire


APP_DIR = Path(__file__).resolve().parent #app directory path
TEMPLATE_DIR = APP_DIR/"app"/"templates" #join path of app directory and template folder for our notification service template (connection config in notf service)
print(TEMPLATE_DIR)



def generate_access_token(data:dict, expiry:timedelta = timedelta(minutes=55)) -> dict:
    token = jwt.encode(
            payload = {
                "data": data,
                "exp" : datetime.now(timezone.utc) + expiry, #utc is a time format, which is supported by jwt, else it cant check if toke has expired
                "jti": str(uuid4()) #assigns unique id to this token
            },
            algorithm=security_settings.JWT_ALGORITHM,
            key=security_settings.JWT_SECRET
        )
    return token
    

def decode_access_token(token:str) -> dict:
    try:
        return jwt.decode(
        jwt = token,
        key=security_settings.JWT_SECRET,
        algorithms = [security_settings.JWT_ALGORITHM]
    )
    except jwt.PyJWTError:
        return None
    
def generate_url_safe_token(data:dict,salt:str | None = None)->str:
    return _serializer.dumps(data,salt=salt)

def decode_url_safe_token(token:str,salt:str | None = None, expiry:timedelta|None = None)->dict | None:
    try:
     return _serializer.loads(token,
                              salt=salt,
                      max_age = expiry.total_seconds() if expiry else None)
    except(BadSignature,SignatureExpired):
        return None #means one of these two error has occured so return type none

