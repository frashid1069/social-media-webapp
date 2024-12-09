from django.urls import path, include
from . import views
from rest_framework import routers






router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    # Comments API
    path('authors/<int:AUTHOR_SERIAL>/posts/<int:POST_SERIAL>/comments', views.comment_list, name='comment_list'),
    path('posts/<path:POST_FQID>/comments', views.comment_list, name='fqid_comment_list'),
    path('authors/<int:AUTHOR_SERIAL>/post/<int:POST_SERIAL>/comment/<path:REMOTE_COMMENT_FQID>', views.comment_detail_post, name='comment-detail'),
    #Commented API
    path('authors/<int:AUTHOR_SERIAL>/commented', views.author_comment_list, name='author_comment_list'),
    path('authors/<path:AUTHOR_FQID>/commented', views.author_comment_list, name='fqid_author_comment_list'),
    path('authors/<int:AUTHOR_SERIAL>/commented/<int:COMMENT_SERIAL>', views.comment_detail, name='comment_detail'),
    path('commented/<path:COMMENT_FQID>', views.comment_detail, name='fqid_comment_detail'),
]