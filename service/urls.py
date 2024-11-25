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
router.register('follow', views.FollowView)

urlpatterns = [
    path("", views.index, name="index"),
    path("login/",views.Login.as_view(), name="login"), 
    path("signup/",views.SignUp.as_view(), name="signup"),
    path('stream/<int:author_id>/editProfile', views.edit_profile, name='edit_profile'),
    path('authors/<int:AUTHOR_SERIAL>/followers', views.get_followers, name='get_followers'),
    path('authors/<int:AUTHOR_SERIAL>/followers/<path:FOREIGN_AUTHOR_FQID>', views.foreign_followers, name='foreign_followers'),
    path('authors/<int:AUTHOR_SERIAL>/inbox', views.inbox, name='inbox'),
    path('forward/', views.forward_follow_request, name="forward_follow_request"),
    path('follows/', views.get_follow_requests, name="get_follow_requests"),
    path('follows/<int:FOLLOW_ID>', views.handle_follow_request, name="handle_follow_request")
]

urlpatterns += router.urls