from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from jwt import exceptions
import jwt
from django.conf import settings


class JwtQueryParamsAuthentication(BaseAuthentication):
    
    def authenticate(self, request):
        
        token = request.query_params.get('token')
        salt = settings.SECRET_KEY
        payload = None
        message = None
        
        try: 
            payload = jwt.decode(token, salt, True)
        except exceptions.ExpiredSignatureError:
            raise AuthenticationFailed({'code':1003, 'error':"token expired"}) 
        except jwt.DecodeError:
            raise AuthenticationFailed({'code':1003, 'error':"failed authentication with the token"}) 

        
        
        return (payload, token)