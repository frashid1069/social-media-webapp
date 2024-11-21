from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from jwt import exceptions
import jwt
from django.conf import settings
from rest_framework import exceptions
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
import base64


class JwtQueryParamsAuthentication(BaseAuthentication):
    
    def authenticate(self, request):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[1]
        else:
            token = request.headers.get('token')
        
        if not token:
            return None
        
        salt = settings.SECRET_KEY
                
        try:
            payload = jwt.decode(token, salt, algorithms="HS256")
            #payload = jwt.decode(token, salt, algorithms="HS256")
            
        except Exception:
            raise exceptions.AuthenticationFailed('Invalid token')

        try:
            if 'id' in payload and 'username' in payload:
                user = User.objects.get(id=payload['id'], username=payload['username'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, token)
    
    
class BackendAuthentication(BaseAuthentication):
    """
    For backend-to-backend communication.
    Backends must include a shared token in headers.
    """

    def authenticate(self, request):
        token = None
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Basic "):
            return None
        salt = f"{request.scheme}://{request.get_host()}/api/"
        
        try:
            payload = jwt.decode(token, salt, algorithms="HS256")
            print(payload)
        except Exception:
            raise exceptions.AuthenticationFailed('Invalid token')

        try:
            user = User.objects.get(username=username)
            
            if not user.check_password(password):
                raise exceptions.AuthenticationFailed("Invalid username or password")
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid username or password")

        # If authentication is successful, return the user and None (no token)
        return (user, None)