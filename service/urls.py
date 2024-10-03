from django.urls import path, include
from . import views
from rest_framework import routers

"""Authors API
URL: ://service/api/authors/
GET [local, remote]: retrieve all profiles on the node (paginated)
    page: how many pages
    size: how big is a page"""

app_name = "service"

urlpatterns = [
    path("", views.index, name="index"),
    
]
#path("api/authors/", views.AuthorsView.as_view(), name="get_authors")
# ~author/$    name: author-list
# ~author/{pk}/$   name: author-detail
router = routers.DefaultRouter()
router.register('author', views.AuthorView)
router.register('post', views.PostView)
router.register('comment', views.CommentView)
router.register('like', views.LikeView)
router.register('follow', views.FollowView)
router.register('inbox', views.InboxView)


urlpatterns += router.urls