import jwt
import datetime
from django.conf import settings


def create_token(payload, timeout=60):
    
    salt = settings.SECRET_KEY
    
    headers = {
        'typ':'jwt',
        'alg':'HS256'
    }
    
    payload['exp'] = datetime.datetime.now() + datetime.timedelta(minutes=timeout)
    
    return jwt.encode(payload=payload, key=salt, algorithm='HS256', headers=headers)

def create_server_token(payload, timeout=60, host=None):
    salt = host
    
    headers = {
        'typ':'jwt',
        'alg':'HS256'
    }
    
    payload['exp'] = datetime.datetime.now() + datetime.timedelta(minutes=timeout)
    
    return jwt.encode(payload=payload, key=salt, algorithm='HS256', headers=headers)