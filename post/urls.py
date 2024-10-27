from django.urls import path, include
from . import views
from rest_framework import routers






router = routers.DefaultRouter()
router.register('post', views.PostView)
router.register('repost', views.RepostView)
urlpatterns = [
    path('', include(router.urls))
]