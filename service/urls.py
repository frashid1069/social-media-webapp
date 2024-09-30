from django.urls import path, include
from . import views

"""Authors API
URL: ://service/api/authors/
GET [local, remote]: retrieve all profiles on the node (paginated)
    page: how many pages
    size: how big is a page"""

app_name = "service"

urlpatterns = [
    path("", views.index, name="index"),
    #path("api/authors/", views.AuthorsView.as_view(), name="get_authors")
]