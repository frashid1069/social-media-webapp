from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
# router.register('post', views.PostView)
router.register('repost', views.RepostView)
urlpatterns = [
    path('', include(router.urls)),
    path('authors/<int:author_id>/posts/', views.post_list, name='post_list'),
    path('authors/<int:author_id>/posts/<int:post_id>', views.post_detail, name='post_detail'),
    path('authors/<int:author_id>/posts/<int:post_id>/image', views.post_image, name='post_image'),
    path('posts/<str:fqid>/image', views.post_image_fqid, name='post_image_fqid'),

    path('posttest/', views.test, name='post-list-create'),  # List and create posts
    path('posttest/<int:pk>/', views.test1, name='post-4'),    # Get details of a single post
]