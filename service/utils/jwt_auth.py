import jwt
import datetime
from django.conf import settings
import base64


def create_token(payload, timeout=60):
    
    salt = settings.SECRET_KEY
    
    headers = {
        'typ':'jwt',
        'alg':'HS256'
    }
    
    payload['exp'] = datetime.datetime.now() + datetime.timedelta(minutes=timeout)
    
    return jwt.encode(payload=payload, key=salt, algorithm='HS256', headers=headers)

def create_server_token(username, password):
    credentials = f"{username}:{password}"
    
    # Encode the credentials as Base64
    base64_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    
    return base64_credentials


def create_hearders(node):
    
    token = create_server_token(node.username, node.password)
    
    headers = {
        "Authorization": f"Basic {token}" 
        }
    
    return headers