from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from . import serializers, models


# Later on, the index function will be used to handle incoming requests to polls/ and it will return the hello world string shown below.
def index(request):
    return render(request, "index.html")

class AuthorView(ModelViewSet):
    queryset = models.Author.objects
    serializer_class = serializers.AuthorSerializer
    
class PostView(ModelViewSet):
    queryset = models.Post.objects
    serializer_class = serializers.PostSerializer

    @action(detail=True, methods=['put'], url_path='edit')
    def edit_post(self, request, pk=None):
        post = self.get_object()  # Get the post object based on the provided pk

        if post.author != request.user:
            return Response({'Error': 'You are not allowed to edit this post.'}, status=status.HTTP_403_FORBIDDEN)
        
        title = request.data.get('title', post.title)  # Get new title if provided
        content = request.data.get('content', post.content)  # Get new content if provided
        
        # Update the post fields
        serializer = self.get_serializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

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
    

    