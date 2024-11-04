from django.urls import path, include
from . import views
from rest_framework import routers



"""Authors API
URL: ://service/api/authors/
GET [local, remote]: retrieve all profiles on the node (paginated)
    page: how many pages
    size: how big is a page"""




router = routers.DefaultRouter()
#router.register('author', views.AuthorView)
#router.register('post', views.PostView)
#router.register('comment', views.CommentView)
router.register('like', views.LikeView)
router.register('follow', views.FollowView)
router.register('inbox', views.InboxView)

urlpatterns = [
    path("", views.index, name="index"),
    path("login/",views.Login.as_view(), name="login"), 
    path("signup/",views.SignUp.as_view(), name="signup"),
    path('stream/<int:author_id>/editProfile', views.edit_profile, name='edit_profile'),
]

urlpatterns += router.urls