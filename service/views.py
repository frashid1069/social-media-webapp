from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from . import serializers, models

# Later on, the index function will be used to handle incoming requests to polls/ and it will return the hello world string shown below.
def index(request):
    return HttpResponse("Hello, world. You're at the service index.")

class AuthorView(ModelViewSet):
    queryset = models.Author.objects
    serializer_class = serializers.AuthorSerializer
    
class PostView(ModelViewSet):
    queryset = models.Post.objects
    serializer_class = serializers.PostSerializer

class CommentView(ModelViewSet):
    queryset = models.Comment.objects
    serializer_class = serializers.CommentSerializer
    
class LikeView(ModelViewSet):
    queryset = models.Like.objects
    serializer_class = serializers.LikeSerializer
    
class FollowView(ModelViewSet):
    queryset = models.Follow.objects
    serializer_class = serializers.LikeSerializer
    
class InboxView(ModelViewSet):
    queryset = models.Inbox.objects
    serializer_class = serializers.LikeSerializer

def create_post(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        content_type = request.POST.get("content_type")
        image_content = request.POST.get("image_content")
        visibility = request.POST.get("visibility")
        author = request.POST.get("author")
        models.Post.objects.create(title=title, content=content, content_type = content_type, image_content = image_content, visbility=visibility, author=author)
    return

def create_comment(request, post_id):
    return

def delete_post(request):
    return

def get_public_posts(request, author_id):
    posts = models.Post.filter(authot=author_id, visibility="public")
    
    return
