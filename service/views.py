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
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

# Later on, the index function will be used to handle incoming requests to polls/ and it will return the hello world string shown below.
def index(request):
    return HttpResponse("Hello, world. You're at the service index.")


class Login(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        try:
            author = models.Author.objects.get(username=username)
            
            # registered author without approval
            if not author.user.is_active:
                return Response({'error': 'Your account is inactive. Please wait for admin approval.'}, status=status.HTTP_403_FORBIDDEN)
            
            # encryption
            # if not check_password(password, author.password):
            #     return Response({'error': 'Incorrect username or password.'}, status=status.HTTP_401_UNAUTHORIZED)
            
            if author.password != password:
                return Response({'error': 'Incorrect username or password.'}, status=status.HTTP_401_UNAUTHORIZED)
            token = create_token({'id': author.user.id, 'username': author.user.username}, 100000)
            print(token)
            return Response({
                'token': token,
                'user': {
                    'id': author.user.id,
                    'username': author.user.username,
                    'display_name': author.display_name,
                }
            }, status=status.HTTP_200_OK)

        except models.Author.DoesNotExist:
            return Response({'error': 'User does not exist. Please sign up.'}, status=status.HTTP_404_NOT_FOUND)

class SignUp(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        serializer = serializers.SignUpSerializer(data=request.data)
        
        if serializer.is_valid():
            
            try:
                author = serializer.save()
                token = create_token({'id': author.user.id, 'username': author.user.username}, 100000000)
                return Response({
                    'message': 'User created successfully.',
                    'token': token,
                    'user': {
                        'id': author.user.id,
                        'username': author.user.username,
                        'display_name': author.display_name,
                    }
                }, status=status.HTTP_201_CREATED)
                
            except IntegrityError:
                return Response({'error': 'A user with that username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        # If the data is invalid, return the serializer errors
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class AuthorView(ModelViewSet):
    authentication_classes = []
    permission_classes = []
    queryset = models.Author.objects
    serializer_class = serializers.AuthorSerializer
    
    @extend_schema(
        summary="Retrieve a list of authors",
        description="Fetches a list of all registered authors.",
        responses={200: serializers.AuthorSerializer(many=True)},
        parameters=[
            OpenApiParameter(name="limit", description="Limit the number of authors", type=int, required=False),
            OpenApiParameter(name="offset", description="Offset for pagination", type=int, required=False),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Retrieve a single author",
        description="Fetch details of a specific author by ID.",
        responses={200: serializers.AuthorSerializer, 404: "Not Found"},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create a new author",
        description="Register a new author with the required details.",
        request=serializers.AuthorSerializer,
        responses={201: serializers.AuthorSerializer, 400: "Bad Request"},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update an author",
        description="Update details of an existing author.",
        request=serializers.AuthorSerializer,
        responses={200: serializers.AuthorSerializer, 400: "Bad Request", 404: "Not Found"},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete an author",
        description="Soft-delete or permanently delete an author by ID.",
        responses={204: None, 404: "Not Found"},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
class PostView(ModelViewSet):
    #authentication_classes = [authentication.JwtQueryParamsAuthentication]
    authentication_classes = []
    queryset = models.Post.objects
    serializer_class = serializers.PostSerializer
    
    
    @extend_schema(
        summary="Retrieve a list of posts",
        description="""
        Retrieve a list of posts, with optional filters. 
        - If `author_id` and `visibility` are provided, only public posts of the author will be returned.
        - If `title` is provided, posts matching the title will be returned.
        - If `following_list` is provided, posts from authors that the user follows will be returned.
        """,
        parameters=[
            OpenApiParameter(name="author_id", description="Filter posts by the author's ID", required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name="visibility", description="Filter posts by visibility (public, friend-only, unlisted)", required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name="title", description="Filter posts by title", required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name="following_list", description="Return posts from authors that the user follows", required=False, type=OpenApiTypes.BOOL),
        ],
        responses={200: serializers.PostSerializer(many=True), 400: "Bad Request"},
    )
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

        # # Gets a list of all public posts made by the author
        # if author_id and visibility:
        #     queryset = queryset.filter(id=author_id, visibility="public").order_by("created_at")
        # # List of all posts made by people that the user follows 
        # elif following_list:
        #     queryset = queryset.filter(id=following_list).order_by("created_at")
        # elif author_id:
        #     queryset = queryset.filter(author__id=author_id)  # Filter the queryset by 'author'
        # elif title:
        #     queryset = queryset.filter(title=title)

        # # ~post/?author_id=<pk>
        # if author_id:
        #     queryset = queryset.filter(author__id=author_id) 
        #~post/?author_id=<pk>&visibility=public
        if author_id and visibility:
            queryset = queryset.filter(visibility="public", author__id=author_id)
        # ~post/?author_id=<pk>&title=<str%str> 
        elif title:
            queryset = queryset.filter(title=title)
        # ~post/?following_list=<anything>
        elif following_list:
            if self.authentication_classes:
                current_author = models.Author.objects.get(user=current_user)
            else:
                current_author = models.Author.objects.get(id=author_id)
            print(current_author)
            followed_by_user = models.Author.objects.filter(followers__follower=current_author)
            print(followed_by_user)
            # followed_by_user is a list of author id who current user followed
            # author__id__in filter the posts that belong to these author, same for visibility__in
            #queryset = queryset.filter(author__id__in=followed_by_user,visibility__in=["unlisted", "friend-only", "public"] )
            queryset = queryset.filter(author__id__in=followed_by_user)
            
        return queryset.order_by("updated_at")
    
    # overwrite default destroy: soft delete
    @extend_schema(
        summary="Soft delete a post",
        description="Mark a post as deleted without removing it from the database.",
        responses={204: None, 404: "Not Found"},
    )
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


    @extend_schema(
        summary="Create a new post",
        description="Create a new post with title, content, and optional image.",
        request=serializers.PostSerializer,
        responses={201: serializers.PostSerializer, 400: "Bad Request"},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="Retrieve a single post",
        description="Fetch the details of a post by its ID.",
        responses={200: serializers.PostSerializer, 404: "Not Found"},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update an existing post",
        description="Update the title, content, or image of an existing post.",
        request=serializers.PostSerializer,
        responses={200: serializers.PostSerializer, 400: "Bad Request", 404: "Not Found"},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
class CommentView(ModelViewSet):
    queryset = models.Comment.objects
    serializer_class = serializers.CommentSerializer
    
    @extend_schema(
        summary="Retrieve a list of comments",
        description="""
        Retrieve a list of comments, with optional filtering. 
        - If `post_id` is provided, only comments for that post will be returned.
        """,
        parameters=[
            OpenApiParameter(name="post_id", description="Filter comments by the post's ID", required=False, type=OpenApiTypes.INT),
        ],
        responses={200: serializers.CommentSerializer(many=True), 400: "Bad Request"},
    )
    def get_queryset(self):
        queryset = super().get_queryset()
        post_id = self.request.query_params.get('post_id')

        # If post_id is provided, filter comments by the post ID
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        return queryset.order_by("created_at")

    @extend_schema(
        summary="Create a new comment",
        description="Create a new comment for a post.",
        request=serializers.CommentSerializer,
        responses={201: serializers.CommentSerializer, 400: "Bad Request"},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a single comment",
        description="Fetch the details of a specific comment by its ID.",
        responses={200: serializers.CommentSerializer, 404: "Not Found"},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update an existing comment",
        description="Update the content of an existing comment.",
        request=serializers.CommentSerializer,
        responses={200: serializers.CommentSerializer, 400: "Bad Request", 404: "Not Found"},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a comment",
        description="Delete a comment by its ID.",
        responses={204: None, 404: "Not Found"},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
class LikeView(ModelViewSet):
    queryset = models.Like.objects
    serializer_class = serializers.LikeSerializer

    @extend_schema(
        summary="Retrieve a list of likes",
        description="""
        Retrieve a list of likes, with optional filtering.
        - If `author_id` and `post_id` are provided, returns likes for a particular post made by the specified author.
        - If `author_id` is provided, returns all likes made by that author.
        - If `post_id` is provided, returns all likes for the specified post.
        """,
        parameters=[
            OpenApiParameter(name="author_id", description="Filter likes by the author's ID", required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name="post_id", description="Filter likes by the post's ID", required=False, type=OpenApiTypes.INT),
        ],
        responses={200: serializers.LikeSerializer(many=True), 400: "Bad Request"},
    )
    def get_queryset(self):
        # Get the base queryset from the parent class
        queryset = super().get_queryset()
        # Extract query parameters from the request
        post_id = self.request.query_params.get('post_id')
        author_id = self.request.query_params.get('author_id')

        # If both 'author_id' and 'post_id' are provided in the request query parameters:
        # Filter the queryset to return likes where both the author ID and post ID match
        # i.e., likes made by a specific author on a specific post.
        # ~post/?author_id=<pk>&post_id=<pk> (likes for a particular post made by a particular author)
        if author_id and post_id:
            queryset = queryset.filter(author__id=author_id, post__id=post_id)

        # If only 'author_id' is provided in the query parameters:
        # Filter the queryset to return all likes made by that specific author.
        # ~post/?author_id=<pk> (all likes made by a particular author)
        elif author_id:
            queryset = queryset.filter(author__id=author_id)
        
        # If only 'post_id' is provided in the query parameters:
        # Filter the queryset to return all likes for the specified post.
        # ~post/?post_id=<pk> (all likes for a particular post)
        elif post_id:
            queryset = queryset.filter(post__id=post_id)

        return queryset.order_by("created_at") # return the filtered queryset
    
    @extend_schema(
        summary="Create a new like",
        description="Create a new like for a post by an author.",
        request=serializers.LikeSerializer,
        responses={201: serializers.LikeSerializer, 400: "Bad Request"},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="Retrieve a single like",
        description="Fetch the details of a like by its ID.",
        responses={200: serializers.LikeSerializer, 404: "Not Found"},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete a like",
        description="Delete a like by its ID.",
        responses={204: None, 404: "Not Found"},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    
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
    # Retrieve the post object that matches the given post_id from the database
    post = models.Post.objects.get(id=post_id)

    # Check if the data provided in the request is valid according to the serializer's validation rules.
    serializer = serializers.Post(post, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data) # # Return the updated post data as a JSON response.
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
        # Retrieve the author and post objects based on the provided author_id and post_id
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

        # If the like exists, delete it
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


'''
The edit_profile function allows the user to edit their profile. The user must be logged in to edit their profile.
'''
def edit_profile(request, author_id):
    author = models.Author.objects.get(id=author_id)
    serializer = serializers.Author(author, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    # Return to ui
    return