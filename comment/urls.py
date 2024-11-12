from django.urls import path, include
from . import views
from rest_framework import routers






router = routers.DefaultRouter()
router.register('comment', views.CommentView)
urlpatterns = [
    path('', include(router.urls)),
    # Comments API
    path('authors/<int:AUTHOR_SERIAL>/inbox', views.create_comment, name='create_comment'),
    path('authors/<int:AUTHOR_SERIAL>/posts/<int:POST_SERIAL>/comments', views.comment_list, name='comment_list'),
    path('posts/<int:POST_SERIAL>/comments', views.comment_list_fqid, name='comment_list_fqid'),
    path('authors/<int:AUTHOR_SERIAL>/post/<int:POST_SERIAL>/comment/<path:COMMENT_FQID>', views.comment_detail, name='comment_detail'),
    #Commented API
    path('authors/<int:AUTHOR_SERIAL>/commented', views.author_comment_list, name='author_comment_list'),
    path('authors/<int:author_fqid>/commented', views.author_comment_list_fqid, name='author_comment_list_fqid'),
    # path('authors/<int:AUTHOR_SERIAL>/commented/<int:comment_id>', views.comment_detail, name='comment_detail'),
    # path('commented/<int:comment_fqid>', views.comment_detail, name='comment_detail'),
]