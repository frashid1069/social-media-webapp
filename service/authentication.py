from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from jwt import exceptions
import jwt
from django.conf import settings
from rest_framework import exceptions
from django.contrib.auth.models import User


class JwtQueryParamsAuthentication(BaseAuthentication):
    
    def authenticate(self, request):
        
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[1]
        else:
            token = request.headers.get('token')
        
        if not token:
            return None
        print()
        salt = settings.SECRET_KEY
        
        try:
            payload = jwt.decode(token, salt, algorithms="HS256")
            #print(payload)
        except Exception:
            raise exceptions.AuthenticationFailed('Invalid token')

        try:
            user = User.objects.get(id=payload['id'], username=payload['username'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, token)
    
class BackendUser:
    """A simple user-like object for backend authentication."""
    def __init__(self, backend_name):
        self.backend_name = backend_name

    @property
    def is_authenticated(self):
        return True 

    def __str__(self):
        return self.backend_name
    
class BackendAuthentication(BaseAuthentication):
    """
    For backend-to-backend communication.
    Backends must include a shared token in headers.
    """

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[1]
        if not token:
            return None
        salt = print(f"{request.scheme}://{request.get_host()}/api/")
        
        try:
            payload = jwt.decode(token, salt, algorithms="HS256")
            print(payload)
        except Exception:
            raise exceptions.AuthenticationFailed('Invalid token')

        try:
            user = User.objects.get(password=payload['password'], username=payload['username'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, token)