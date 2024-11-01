from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('image_post', views.ImagePostView)
urlpatterns = [
    path('', include(router.urls)),
    path('image_post/image/', views.get_image, name='get_image'),
    
]