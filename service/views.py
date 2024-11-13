from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from service.utils.jwt_auth import create_token
from django.contrib.auth.hashers import make_password, check_password
from . import authentication, serializers, models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from author.models import Author
from post.models import Post
from service.models import Follow
from rest_framework.permissions import AllowAny
from author.serializers import AuthorSerializer
from like.serializers import LikeSerializer
from comment.serializer import CommentSerializer

# Later on, the index function will be used to handle incoming requests to polls/ and it will return the hello world string shown below.
def index(request):
    return render(request, 'index.html')


class Login(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        try:
            author = Author.objects.get(username=username)
            
            # registered author without approval
            if not author.user.is_active:
                return Response({'error': 'Your account is inactive. Please wait for admin approval.'}, status=status.HTTP_403_FORBIDDEN)
            
            if not check_password(password, author.user.password):
                 return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)
            
            token = create_token({'id': author.user.id, 'username': author.user.username}, 100000)

            return Response({
                'token': token,
                'user': {
                    'id': author.user.id,
                    'username': author.user.username,
                    'display_name': author.display_name,
                }
            }, status=status.HTTP_200_OK)

        except Author.DoesNotExist:
            return Response({'error': 'User does not exist. Please sign up.'}, status=status.HTTP_404_NOT_FOUND)

class SignUp(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
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
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class FollowView(ModelViewSet):
    queryset = models.Follow.objects
    serializer_class = serializers.FollowSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        author_id = self.request.query_params.get('author_id')
        pending =  self.request.query_params.get('pending')
        follower = self.request.query_params.get("follower")
        # Query is a list of all follow requests that are pending, used for notifying user of them 
        if author_id and pending:
            queryset = queryset.filter(followed=author_id, pending=pending)
        if author_id and follower:
            queryset = queryset.filter(followed=author_id, follower=follower)
        return queryset
    

@api_view(['GET'])
def get_followers(request, pk):
    '''
    URL: ://service/api/authors/{AUTHOR_SERIAL}/followers
        GET [local, remote]: get a list of authors who are AUTHOR_SERIAL's followers
    TODO:URL: ://service/api/authors/{AUTHOR_SERIAL}/followers/{FOREIGN_AUTHOR_FQID}

        Note: foreign author ID should be a percent encoded URL of the foreign author. An example URL would be:
            http://example-node-1/api/authors/178aba49-ca39-4741-b227-f40d072b1222/followers/http%3A%2F%2Fexample-node-2%2Fauthors%2F5f57808f-0bc9-4b3d-bdd1-bb07c976d12d
        DELETE [local]: remove FOREIGN_AUTHOR_FQID as a follower of AUTHOR_SERIAL (must be authenticated)
        PUT [local]: Add FOREIGN_AUTHOR_FQID as a follower of AUTHOR_SERIAL (must be authenticated)
        GET [local, remote] check if FOREIGN_AUTHOR_FQID is a follower of AUTHOR_SERIAL
            Should return 404 if they're not
            This is how you can check if follow request is accepted
    '''
    try:
        author = Author.objects.get(id=pk)
        followers = author.followers_authors.all()

        authors = [follow.follower for follow in followers]
        serialized_followers = AuthorSerializer(authors, many=True)
        return Response({
            "type": "followers",
            "followers": serialized_followers.data
        })
    except Author.DoesNotExist:
        return Response({"detail": "Author not found."}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
def send_follow_request(request, pk):
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/inbox
        POST [remote]: send a follow request to AUTHOR_SERIAL
            AUTHOR_SERIAL will be the object below
    """
    try:
        object_author = Author.objects.get(id=pk)
        
        try:
            actor_author = request.user.author
        except Author.DoesNotExist:
            return Response({"detail": "Actor author not found."}, status=status.HTTP_404_NOT_FOUND)

        follow_exists = Follow.objects.filter(follower=actor_author, followed=object_author).exists() # already followed
        mutual_follow = Follow.objects.filter(follower=object_author, followed=actor_author).exists() # becomes friend if object author followed actor

        if follow_exists and mutual_follow:
            return Response({"detail": "Authors are already friends."}, status=status.HTTP_200_OK)
        elif follow_exists:
            return Response({"detail": "Follow request already exists."}, status=status.HTTP_409_CONFLICT)
        elif mutual_follow:
            Follow.objects.create(follower=actor_author, followed=object_author, pending='no')
            return Response({"detail": f"You are now friends of {object_author.display_name}"}, status=status.HTTP_201_CREATED)

        Follow.objects.create(follower=actor_author, followed=object_author, pending='yes')

        response_data = {
            "type": "follow",
            "summary": f"{actor_author.display_name} wants to follow {object_author.display_name}",
            "actor": AuthorSerializer(actor_author).data,
            "object": AuthorSerializer(object_author).data,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    except Author.DoesNotExist:
        return Response({"detail": "Recipient author not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def inbox(request, AUTHOR_SERIAL):
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/inbox
    1) POST [remote]: send a like object to AUTHOR_SERIAL}
    Body is like object
    2) POST [remote]: comment on a post by AUTHOR_SERIAL
    Body is a comment object
    3) POST [remote]: send a follow request to AUTHOR_SERIAL
    AUTHOR_SERIAL will be the object below
    4) receives all the new posts from who you follow
    """
    
    author = get_object_or_404(Author, serial=AUTHOR_SERIAL)
    try: 
        type = request.data.get('type')
    except:
        return Response({"error": "Type is not found in the feild."}, status=status.HTTP_400_BAD_REQUEST)
    
    if type == 'like':
        object = request.data.get("object")
        if object is not None and author.fqid in object:
            sender_host = request.data.get("author", {}).get("host")
            if sender_host == author.host:
                sender = get_object_or_404(Author, fqid=request.data.get("author", {}).get("id"))

            # else:
            # create an author
        
            serializer = LikeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(author=sender)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"error": "Object doesn't matched with AUTHOR_SERIAL"},status=status.HTTP_400_BAD_REQUEST)
    
    elif type == 'follow':
        print("follow")

    elif type == 'comment':
        post = request.data.get("post")
        print(author.fqid)
        if post is not None and author.fqid in post:
            sender_host = request.data.get("author", {}).get("host")
            post = get_object_or_404(Post, fqid=post)
            if sender_host == author.host:
                sender = get_object_or_404(Author, fqid=request.data.get("author", {}).get("id"))
            # else:
            # create an author
        
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(author=sender, post=post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"error": "Post doesn't matched with AUTHOR_SERIAL"},status=status.HTTP_400_BAD_REQUEST)
    
    elif type == 'post':
        sender = request.data.get("author", {}).get("displayName")
        print(f"Received a new post from {sender}")
        return Response(status=status.HTTP_200_OK)
        
    
    return Response({"error": "Nothing matched"},status=status.HTTP_400_BAD_REQUEST)


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
        Post.objects.create(title=title, content=content, content_type = content_type, image_content = image_content, visbility=visibility, author=author)
    # Need to return to the ui page
    return

"""
Creates comment for the post and saves it in the database
"""
def create_comment(request, post_id, author_id):
    if request.method == "POST":
        content = request.POST.get("content")
        post = Post.objects.get(id=post_id)
        author = Author.objects.get(id=author_id)
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
    Post.objects.filter(id=post_id).delete()
    # Return to ui
    return

def edit_post(request, post_id):
    # Retrieve the post object that matches the given post_id from the database
    post = Post.objects.get(id=post_id)

    # Check if the data provided in the request is valid according to the serializer's validation rules.
    serializer = serializers.Post(post, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data) # # Return the updated post data as a JSON response.
    # Return to ui
    return 

def follow_author(request, author_id):
    follower = Author.objects.get(id=author_id)
    followed_id = request.POST.get("followed")
    followed = Author.objects.get(id=followed_id)

    # Check if a pending follow request already exists
    existing_follow = Follow.objects.filter(follower=follower, followed=followed, pending="yes")
    if existing_follow:
        return
    
    # Create a new follow request if none exists
    Follow.objects.create(follower=follower, followed=followed, pending="yes")
    return

def handle_follow(request, follow_id):
    # From https://stackoverflow.com/questions/3805958/how-to-delete-a-record-in-django-models by Wolph
    choice = request.POST.get("choice")
    follow = Follow.objects.filter(id=follow_id).first()

    # if doesn't exist, return
    if not follow:
        return

    # if follow request declined, delete the follow object entirely
    if choice == "no":
        follow.delete()
    # If accepted, update and save follow object to show that the sender is following the receiver    
    elif choice == "yes":
        follow.pending = "no"
        follow.save()
    # Return to ui
    return

def unfollow_author(request, author_id):
    current_user_author = request.user.author  # Retrieve the current user's Author instance
    author_to_unfollow = Author.objects.get(id=author_id)
    
    # Check if the Follow relationship exists
    follow_instance = Follow.objects.filter(follower=current_user_author, followed=author_to_unfollow)
    if follow_instance:
        follow_instance.delete()  # Remove the Follow relationship
    return


def create_like(request, author_id, post_id):
    if request.method == "POST":
        # Retrieve the author and post objects based on the provided author_id and post_id
        author = Author.objects.get(id=author_id)
        post = Post.objects.get(id=post_id)

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
    following_posts = Post.filter(author=following_authors)
    return

def sign_up(request):
    username = request.POST.get("username")
    display_name = request.POST.get("display_name")
    password = request.POST.get("password")
    bio = request.POST.get("bio")
    github_url = request.POST.get("github_url")
    # From https://www.devhandbook.com/django/user-profile/
    profile_image = request.POST.get("profile_image")
    Author.objects.create(username=username, display_name=display_name, password=password, bio=bio, github_url=github_url, profile_image=profile_image)
    # Return to UI
    return 

def login(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    author = Author.objects.get(username=username)
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
    author = Author.objects.get(id=author_id)
    serializer = AuthorSerializer(author, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    # Return to ui
    return


    