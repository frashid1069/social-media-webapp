from django.urls import path
from .views import chatgpt_response

urlpatterns = [
    path('chat/', chatgpt_response, name='chat_response'),
]