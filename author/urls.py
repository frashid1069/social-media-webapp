from django.urls import path, include
from .views import AuthorView
from rest_framework import routers

author_list = AuthorView.as_view({
    'get': 'list'
})
author_detail = AuthorView.as_view({
    'get': 'retrieve',
    'put': 'update'
})

urlpatterns = [
    path('authors/', author_list, name='author-list'),
    path('authors/<int:pk>/', author_detail, name='author-detail'),
]