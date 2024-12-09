from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('post', views.PostView)
urlpatterns = [
    path('', include(router.urls)),
    # post api
    path('authors/<int:AUTHOR_SERIAL>/posts/', views.post_list, name='post_list'),
    path('authors/<int:AUTHOR_SERIAL>/posts/<int:POST_SERIAL>', views.post_detail, name='post_detail'),
    path('posts/<path:POST_FQID>/image', views.post_image, name='fqid_post_image'),
    path('posts/<path:POST_FQID>', views.fqid_post_detail, name='fqid_post_detail'),
    # image post api
    path('authors/<int:AUTHOR_SERIAL>/posts/<int:POST_SERIAL>/image', views.post_image, name='post_image'),
    path('posts/', views.get_all_visible_post, name='get_all_visible_post')
]

