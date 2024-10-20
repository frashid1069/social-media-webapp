from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from service.utils.jwt_auth import create_token
# from django.contrib.auth.hashers import make_password, check_password
from . import authentication, serializers, models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import IntegrityError

# Later on, the index function will be used to handle incoming requests to polls/ and it will return the hello world string shown below.
def index(request):
    return HttpResponse("Hello, world. You're at the service index.")


class Login(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        author = models.Author.objects.get(username=username,password=password)
        try:
            author = models.Author.objects.get(username=username)
            # if not check_password(password, author.password):
            #     return Response({'error': 'Incorrect username or password.'}, status=status.HTTP_401_UNAUTHORIZED)
            if author.password != password:
                return Response({'error': 'Incorrect username or password.'}, status=status.HTTP_401_UNAUTHORIZED)
            token = create_token({'id': author.id, 'name': author.username}, 100000)
            print(token)
            return Response({
                'token': token,
                'user': {
                    'id': author.id,
                    'username': author.username,
                }
            }, status=status.HTTP_200_OK)

        except models.Author.DoesNotExist:
            return Response({'error': 'User does not exist. Please sign up.'}, status=status.HTTP_404_NOT_FOUND)

class SignUp(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
    
        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.create_user(username=username, password=password)
            token = create_token({'id':user.id, 'username':user.username}, 100000000)
            
            return Response({
                'message': 'User created successfully.',
                'token':token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                }
            }, status=status.HTTP_201_CREATED)
            
        except IntegrityError:
            return Response({'error': 'A user with that username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AuthorView(ModelViewSet):
    queryset = models.Author.objects
    serializer_class = serializers.AuthorSerializer
    
    # authentication_classes = [auth.JwtQueryParamsAuthentication]
    
class PostView(ModelViewSet):
    queryset = models.Post.objects
    serializer_class = serializers.PostSerializer
    # overwrite the default get_queryset
    def get_queryset(self):
        queryset = super().get_queryset()  
        
        # assume current user is the author, return AnonymousUser if not logged in
        current_user = self.request.user
        # Only return not deleted post
        is_deleted = False
        queryset = queryset.filter(is_deleted=is_deleted)
        author_id = self.request.query_params.get('author_id')  
        visibility = self.request.query_params.get("visibility")
        title = self.request.query_params.get('title')
        following_list = self.request.query_params.get("following_list")
        # Gets a list of all public posts made by the author
        if author_id and visibility:
            queryset = queryset.filter(id=author_id, visibility="public").order_by("created_at")
        # List of all posts made by people that the user follows 
        elif following_list:
            queryset = queryset.filter(id=following_list).order_by("created_at")
        elif author_id:
            queryset = queryset.filter(author__id=author_id)  # Filter the queryset by 'author'
        elif title:
            queryset = queryset.filter(title=title)

        # ~post/?author_id=<pk>
        if author_id:
            queryset = queryset.filter(author__id=author_id, title=title) 
        # ~post/?author_id=<pk>&title=<str%str> 
        if title:
            queryset = queryset.filter(title=title)
        # ~post/?following_list=<True/False>
        if following_list:
            followed_by_user = models.Author.objects.filter(followers__follower=current_user)
            # followed_by_user is a list of author id who author followed
            # author__id__in filter the posts that belong to these author, same for visibility__in
            queryset = queryset.filter(author__id__in=followed_by_user,visibility__in=["unlisted", "friend-only"] )
            
        return queryset.order_by("created_at")
    
    # overwrite default destroy: soft delete 
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

class CommentView(ModelViewSet):
    queryset = models.Comment.objects
    serializer_class = serializers.CommentSerializer
    
class LikeView(ModelViewSet):
    queryset = models.Like.objects
    serializer_class = serializers.LikeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        post_id = self.request.query_params.get('post_id')
        author_id = self.request.query_params.get('author_id')

        # ~post/?author_id=<pk>&post_id=<pk> (likes for a particular post made by a particular author)
        if author_id and post_id:
            queryset = queryset.filter(author__id=author_id, post__id=post_id)
        # ~post/?author_id=<pk> (all likes made by a particular author)
        elif author_id:
            queryset = queryset.filter(author__id=author_id)
        # ~post/?post_id=<pk> (all likes for a particular post)
        elif post_id:
            queryset = queryset.filter(post__id=post_id)

        return queryset.order_by("created_at")
    
class FollowView(ModelViewSet):
    queryset = models.Follow.objects
    serializer_class = serializers.LikeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        author_id = self.request.query_params.get('author_id')
        pending =  self.request.query_params.get('pending')
        # Query is a list of all follow requests that are pending, used for notifying user of them 
        if author_id and pending:
            queryset = queryset.filter(followed=author_id, pending=pending)
    
class InboxView(ModelViewSet):
    queryset = models.Inbox.objects
    serializer_class = serializers.LikeSerializer

"""
Creates a post and saves it in the database
"""
def create_post(request):
    # Checks if request is a POST, then gets information and creates the post
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        content_type = request.POST.get("content_type")
        image_content = request.POST.get("image_content")
        visibility = request.POST.get("visibility")
        author = request.POST.get("author")
        models.Post.objects.create(title=title, content=content, content_type = content_type, image_content = image_content, visbility=visibility, author=author)
    # Need to return to the ui page
    return

"""
Creates comment for the post and saves it in the database
"""
def create_comment(request, post_id, author_id):
    if request.method == "POST":
        content = request.POST.get("content")
        post = models.Post.objects.get(id=post_id)
        author = models.Author.objects.get(id=author_id)
        if content == None or len(content) == 0:
            # Error return to page again, does not create comment
            return 
        # Creates comment
        models.Comment.objects.create(content=content, post=post, author=author_id)
    # Redirect to page here, comment is added now
    return

def delete_post(request, post_id):
    # Request should send through post id
    # From https://stackoverflow.com/questions/3805958/how-to-delete-a-record-in-django-models by Wolph
    models.Post.objects.filter(id=post_id).delete()
    # Return to ui
    return

# Now in PostView
# def get_public_posts(request, author_id):
#     posts = models.Post.filter(id=author_id, visibility="public")
#     posts = posts.order_by("created_at")
#     # Return to the ui page, pass through the list of posts above
#     return

def edit_post(request, post_id):
    post = models.Post.objects.get(id=post_id)
    serializer = serializers.Post(post, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    # Return to ui
    return 

def follow_author(request, author_id):
    follower = models.Author.objects.get(id=author_id)
    followed = request.POST.get("followed")
    models.Follow.objects.create(follower=follower, followed=followed)
    # Return to page now
    return

def handle_follow(request, follow_id):
    if request.get("choice") == "no":
        # From https://stackoverflow.com/questions/3805958/how-to-delete-a-record-in-django-models by Wolph
        models.Follow.objects.filter(id=follow_id).delete()
    else:
        follow = models.Follow.get(id=follow_id)
        follow["pending"] = "no"
        follow.save()
    # Return to ui
    return

def create_like(request, author_id, post_id):
    if request.method == "POST":
        author = models.Author.objects.get(id=author_id)
        post = models.Post.objects.get(id=post_id)

        # Check if the like already exists
        if models.Like.objects.filter(author=author, post=post).exists():
            return
        # Create the like
        models.Like.objects.create(author=author, post=post)

    # Redirect to the UI
    return

def delete_like(request, author_id, post_id):
    if request.method == "DELETE":
        like = models.Like.objects.filter(post=post_id, author=author_id)
        if like.exists():
            like.delete()
    # Return to ui
    return


def get_stream_posts(request, author_id):
    following = models.Follow.filter(follower=author_id)
    following_authors = []
    for follow in following:
        follower = follow.get_follower()
        following_authors.append(follower)
    # A list of all posts made by people that the author is following 
    following_posts = models.Post.filter(author=following_authors)
    return

def sign_up(request):
    username = request.POST.get("username")
    display_name = request.POST.get("display_name")
    password = request.POST.get("password")
    bio = request.POST.get("bio")
    github_url = request.POST.get("github_url")
    # From https://www.devhandbook.com/django/user-profile/
    profile_image = request.POST.get("profile_image")
    models.Author.objects.create(username=username, display_name=display_name, password=password, bio=bio, github_url=github_url, profile_image=profile_image)
    # Return to UI
    return 

def login(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    author = models.Author.objects.get(username=username)
    if author == None:
        # User does not exist return
        return 
    if author.password != password:
        # Invalid password return
        return
    # Successful return, return with username to show they are signed in now
    return
# Now in the followView 
# def notify(request, author_id):
#     follow_requests = models.Follow.filter(following=author_id)
#     return
