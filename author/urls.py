from django.urls import path, include
from .views import AuthorView
from . import views
from rest_framework import routers

author_list = AuthorView.as_view({
    'get': 'list'
})
author_detail = AuthorView.as_view({
    'put': 'update'
})

urlpatterns = [
    path('authors/', author_list, name='author-list'),
    path('authors/<int:AUTHOR_SERIAL>/', views.author_detail, name='author-detail'),
    path('authors/<path:AUTHOR_FQID>/', views.author_detail, name='fqid-author-detail'),
]