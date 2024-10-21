from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from jwt import exceptions
import jwt
from django.conf import settings
from rest_framework import exceptions
from django.contrib.auth.models import User


class JwtQueryParamsAuthentication(BaseAuthentication):
    
    def authenticate(self, request):
        
        token = request.headers.get('token')
        salt = settings.SECRET_KEY
        

        try:
            payload = jwt.decode(token, salt, algorithms="HS256")
            print(payload)
        except Exception:
            raise exceptions.AuthenticationFailed('Invalid token')

        try:
            user = User.objects.get(id=payload['id'], username=payload['username'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, token)