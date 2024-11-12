from django.urls import path, include
from . import views
from rest_framework import routers


urlpatterns = [
    # TODO: Inbox
    #path('authors/<int:author_id>/inbox', views.inbox_like, name='inbox_like'),
    path('authors/<int:AUTHOR_SERIAL>/posts/<int:POST_SERIAL>/likes', views.who_liked_this_post, name='liked_post'),
    path('posts/<path:POST_FQID>/likes', views.who_liked_this_post, name='fqid_liked_post'),
    path('authors/<int:AUTHOR_SERIAL>/posts/<int:POST_SERIAL>/comments/<path:COMMENT_FQID>/likes', views.who_liked_this_comment, name='liked_comment'),
    
    # list of likes
    path('authors/<int:AUTHOR_SERIAL>/liked', views.things_liked_by_author, name='things_liked_by_author'),
    path('authors/<path:AUTHOR_FQID>/liked', views.things_liked_by_author, name='things_liked_by_author_fqid'),
    
    # single like
    path('authors/<int:AUTHOR_SERIAL>/liked/<int:LIKE_SERIAL>', views.like_detail, name='like_detail'),
    path('liked/<path:LIKE_FQID>', views.like_detail, name='fqid_like_detail'),
]