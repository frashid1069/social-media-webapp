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
from service.serializers import Follow, FollowSerializer
from rest_framework.permissions import AllowAny
from author.serializers import AuthorSerializer
from like.serializers import LikeSerializer
from comment.serializer import CommentSerializer, Comment
from post.serializers import PostSerializer
import urllib.parse
import requests
from rest_framework.exceptions import ValidationError
from service.models import Node
from service.utils.jwt_auth import create_hearders

# Later on, the index function will be used to handle incoming requests to polls/ and it will return the hello world string shown below.
def index(request):
    return render(request, 'index.html')


class Login(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def post(self, request):
        """
        Handles user login by verifying credentials and generating an authentication token.

        Method:
        - POST: Authenticates a user and returns a token along with user information.

        Behavior:
        1. Retrieves `username` and `password` from the request data.
        2. Checks for the existence of a user with the given `username`.
        - If the user is not found, returns HTTP 404 with an error message.
        3. Verifies if the user's account is active:
        - If not active, returns HTTP 403 with a message indicating the account requires admin approval.
        4. Validates the provided password against the stored password:
        - If invalid, returns HTTP 401 with an error message.
        5. Generates an authentication token for the user, with a payload containing:
        - The author's serial ID.
        - The user's username.
        - Token validity is set for 100,000 seconds.
        6. Returns HTTP 200 with:
        - A valid authentication token.
        - User details including:
            - Author ID (serial).
            - Username.
            - Display name.
            - Serialized author information.

        Parameters:
        - `username`: The username provided in the request.
        - `password`: The password provided in the request.

        Returns:
        - HTTP 200 with token and user information if login is successful.
        - HTTP 403 if the user's account is inactive.
        - HTTP 401 if the provided credentials are invalid.
        - HTTP 404 if the user does not exist.
        """
        username = request.data.get("username")
        password = request.data.get("password")
        try:
            user = User.objects.get(username=username)
            
            # registered author without approval
            if not user.is_active:
                return Response({'error': 'Your account is inactive. Please wait for admin approval.'}, status=status.HTTP_403_FORBIDDEN)
            
            if not check_password(password, user.password):
                 return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)
            
            token = create_token({'id': user.author.serial, 'username': user.username}, 100000)

            return Response({
                'token': token,
                'user': {
                    'id': user.author.serial,
                    'username': user.username,
                    'display_name': user.author.display_name,
                    "author": AuthorSerializer(user.author).data
                }
            }, status=status.HTTP_200_OK)

        except Author.DoesNotExist:
            return Response({'error': 'User does not exist. Please sign up.'}, status=status.HTTP_404_NOT_FOUND)

class SignUp(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Handles user registration and account creation.

        Method:
        - POST: Accepts user data, validates it, and creates a new account.

        Behavior:
        1. Accepts user data from the request, including:
        - Username
        - Password
        - Display name
        - Any other necessary fields as defined in `SignUpSerializer`.
        2. Validates the provided data using the `SignUpSerializer`:
        - If the data is invalid, returns HTTP 400 with validation error messages.
        3. On successful validation:
        - Saves the user and creates an associated author record.
        - Generates an authentication token with the following payload:
            - Author serial ID (`id`).
            - Username.
            - Token validity is set for 100,000,000 seconds.
        - Returns HTTP 201 with:
            - A success message.
            - A valid authentication token.
            - Basic user details:
            - Author ID (serial).
            - Username.
            - Display name.
        4. Handles validation errors during save:
        - If an error occurs, returns HTTP 400 with the error details.

        Authentication and Permissions:
        - `authentication_classes`: Empty, as this endpoint does not require authentication.
        - `permission_classes`: Set to `AllowAny`, allowing access to anyone.

        Parameters:
        - User data as per the serializer requirements.

        Returns:
        - HTTP 201 with user details and a token if account creation is successful.
        - HTTP 400 with validation errors if the data is invalid.
        - HTTP 400 with detailed errors if an error occurs during save.
        """

        serializer = serializers.SignUpSerializer(data=request.data, context={'host': request.build_absolute_uri('/')})
        if serializer.is_valid():
            try:
                author = serializer.save()
                token = create_token({'id': author.serial, 'username': author.user.username}, 100000000)
                return Response({
                    'message': 'User created successfully.',
                    'token': token,
                    'user': {
                        'id': author.serial,
                        'username': author.user.username,
                        'display_name': author.display_name,
                    }
                }, status=status.HTTP_201_CREATED)
                
            except ValidationError as e:
                return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
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
    
@api_view(['POST', 'DELETE'])
def forward_follow_request(request):
    """
    Handles forwarding follow requests and managing follow relationships.

    Methods:
    1. **POST**: Sends a follow request from the authenticated user to another author.
    - If the authors are already friends, returns a success message.
    - If a follow request already exists or the user is already following the target author, returns a conflict message.
    - Creates a `Follow` object with:
        - `pending='no'` if the target author is on a remote node and the node is trusted.
        - `pending='yes'` otherwise.
    - Forwards the follow request to the target author's inbox if the target is on a remote node.

    2. **DELETE**: Sends an unfollow request from the authenticated user to another author.
    - If the follow relationship exists, it is removed.
    - If the unfollow action is successful, returns a success message.
    - Otherwise, returns an error message.

    Behavior:
    - Validates the `type` field in the request data.
    - Ensures that only non-staff users can perform this operation (local API only).
    - Manages follow relationships for both local and remote nodes.

    Parameters:
    - `type`: Must be set to `"follow"`.
    - `object`: Contains the target author's details (either as a full object or an FQID).

    Returns:
    - POST:
    - HTTP 201 with follow request details if successful.
    - HTTP 409 if a follow request already exists or the user is already following the target author.
    - HTTP 400 if the target node rejects the request or if the follow relationship cannot be created.
    - DELETE:
    - HTTP 200 if the unfollow action is successful.
    - HTTP 400 if the unfollow action fails.
    - HTTP 403 if the operation is attempted by a staff user.
    - HTTP 400 if the `type` is not `"follow"` or if required fields are missing.

    Special Cases:
    - Handles follow requests for remote nodes:
    - Ensures the target node is trusted (`Node.is_allowed=True`).
    - Forwards follow requests to the target node's inbox.
    - Supports rejection of follow requests by deleting the `Follow` object.
    """

    if request.user.is_staff:
        return Response({"error": "Local api only"}, status=status.HTTP_403_FORBIDDEN)
    
    actor = request.user.author
    try: 
        type = request.data.get('type')
    except:
        return Response({"error": "Type is not found in the feild."}, status=status.HTTP_400_BAD_REQUEST)
    
    if type == 'follow':
        # send follow request
        if request.method == 'POST':
            # create the object author's object if author doesn't exist
            object = get_or_create_copy_author_object(request.data.get("object", {}))
            
            follow_exists = Follow.objects.filter(follower=actor, followed=object, pending='no').exists() # already followed
            unapproved_follow_exists = Follow.objects.filter(follower=actor, followed=object, pending='yes').exists() # not yet approved
            mutual_follow = Follow.objects.filter(follower=object, followed=actor, pending='no').exists() # object author followed current already

            if follow_exists and mutual_follow:
                return Response({"detail": "Authors are already friends."}, status=status.HTTP_200_OK)
            elif follow_exists:
                return Response({"detail": "Already following."}, status=status.HTTP_409_CONFLICT)
            elif unapproved_follow_exists:
                return Response({"detail": "Follow request already exists."}, status=status.HTTP_409_CONFLICT)

            # assuming following for remote nodes and not for local
            nodes_exists = Node.objects.filter(is_allowed=True, url=object.host).exists()
            if nodes_exists:
                Follow.objects.create(follower=actor, followed=object, pending='no')
            else:
                Follow.objects.create(follower=actor, followed=object, pending='yes')

            response_data = {
                "type": "follow",
                "summary": f"{actor.display_name} wants to follow {object.display_name}",
                "actor": AuthorSerializer(actor).data,
                "object": AuthorSerializer(object).data,
            }
            
            # forward follow request
            if object.host != actor.host:            
                if nodes_exists:
                    node = Node.objects.get(is_allowed=True, url=object.host)                
                    print(node.username, node.password)
                    headers = create_hearders(node)
                    try:
                        response = requests.post(f"{object.fqid}/inbox", headers=headers, json=request.data)
                        
                        if response.status_code == 201 or response.status_code == 200:
                            try:
                                response_data = response.json()
                                
                            except ValidationError as e:
                                print(f"Validation Error: {e.detail}")
                                return Response({"error": e.detail},  status=status.HTTP_400_BAD_REQUEST)
                        else:
                            print(f"Failed POST request to {node.url} with {response}")
                            return Response(f"Failed POST request to  {node.url} with {response}", status=status.HTTP_400_BAD_REQUEST)
                            
                    except requests.RequestException as e:
                        print(f"Error forward follow request to {node.url}: {e}")
                else:
                    print(f"Error fetching from {node.url}")

            return Response(response_data, status=status.HTTP_201_CREATED)

        # unfollow request
        elif request.method == 'DELETE':
            object_fqid = request.data.get("object", {}).get("id")
            object_author = get_object_or_404(Author, fqid=object_fqid, is_deleted=False)
            
            follow_object = get_object_or_404(Follow, follower=actor, followed=object_author)
            follow_object.reject()
            if not Follow.objects.filter(follower=actor, followed=object_author).exists():
                return Response({"detail": "Reject the follow request"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to reject the follow request"}, status=status.HTTP_400_BAD_REQUEST)
            
    return Response({"error": "Type is not follow."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_follow_requests(request):
    """
    Retrieves all pending follow requests for the authenticated user.

    URL Pattern:
    - GET: Fetches follow requests where the authenticated user is the target (followed) author.

    Behavior:
    1. Retrieves follow requests for the authenticated user (`request.user.author`).
    2. Filters the `Follow` objects to include only those with:
    - `followed` set to the authenticated user.
    - `pending='yes'` (indicating the request is awaiting approval).
    3. Serializes the filtered follow requests and returns them.

    Returns:
    - HTTP 200 with a list of serialized follow requests if successful.
    - Each follow request contains details about:
    - The follower.
    - The followed author.
    - Any additional metadata included in the `FollowSerializer`.

    Special Cases:
    - Ensures that only pending follow requests are included in the response.
    - Requires the user to be authenticated and associated with an author object.
    """
    author = request.user.author
    follow_requests = Follow.objects.filter(followed=author, pending='yes')
    serializers = FollowSerializer(follow_requests, many=True)
    return Response(serializers.data)

@api_view(['PUT'])
def handle_follow_request(request, FOLLOW_ID=None):
    """
    Handles the acceptance or rejection of a follow request.

    URL Pattern:
    - PUT: Updates the status of a pending follow request identified by `FOLLOW_ID`.

    Behavior:
    1. Retrieves the `Follow` object identified by `FOLLOW_ID` with:
    - `pending="yes"` (indicating the request is awaiting approval).
    2. Checks the `pending` field in the request data:
    - If `pending="yes"`:
        - Rejects the follow request by removing the `Follow` object.
        - Returns HTTP 204 with a success message.
    - If `pending="no"`:
        - Accepts the follow request by updating the `Follow` object to `pending="no"`.
        - Returns HTTP 200 with a success message.
    - If the `pending` field is invalid or missing:
        - Returns HTTP 400 with an error message.

    Parameters:
    - FOLLOW_ID: The ID of the follow request to be handled.
    - `pending` (in request data): Indicates the decision for the follow request:
    - `"yes"` to reject the request.
    - `"no"` to accept the request.

    Returns:
    - HTTP 200 if the follow request is accepted.
    - HTTP 204 if the follow request is rejected.
    - HTTP 400 if:
    - The `FOLLOW_ID` is invalid.
    - The `pending` field is invalid or missing.
    - HTTP 404 if the follow request does not exist or is not pending.

    Special Cases:
    - Ensures that only pending follow requests (`pending="yes"`) can be handled.
    - Handles both acceptance and rejection with appropriate feedback.
    """
    if FOLLOW_ID is not None:
        follow = get_object_or_404(Follow, id=FOLLOW_ID, pending="yes")
        decision = request.data.get("pending")
        if decision == "yes":
            follow.reject()
            return Response({"detail": "Follow request rejected."}, status=status.HTTP_204_NO_CONTENT)
        elif decision == "no":
            follow.accept()
            return Response({"detail": "Follow request accepted."}, status=status.HTTP_200_OK)         
        else:
            return Response({"error": "Feild pending should be yes/no."}, status=status.HTTP_400_BAD_REQUEST)
        
    return Response({"error": "Incorret follow id ."}, status=status.HTTP_400_BAD_REQUEST)
            
        
@api_view(['GET'])
def get_followers(request, AUTHOR_SERIAL=None):
    """
    Retrieves a list of followers for a specific author.

    URL Pattern:
    - ://service/api/authors/{AUTHOR_SERIAL}/followers
    Example:
    - http://localhost:8000/api/authors/2/followers
    - GET [local, remote]: Retrieves a list of authors who are followers of the author identified by `AUTHOR_SERIAL`.

    Behavior:
    1. Fetches the author identified by `AUTHOR_SERIAL`.
    - Ensures the author exists and is not marked as deleted (`is_deleted=False`).
    - Returns HTTP 404 if the author is not found.
    2. Retrieves all `Follow` objects where:
    - `followed` is the specified author.
    - Follows may be pending or accepted.
    3. Extracts the list of follower authors from the `Follow` objects.
    4. Serializes the list of followers using the `AuthorSerializer`.
    5. Returns the serialized list of followers with the following structure:
    - `"type"`: Always set to `"followers"`.
    - `"followers"`: A list of serialized follower author data.

    Parameters:
    - AUTHOR_SERIAL: Numeric identifier for the author.

    Returns:
    - HTTP 200 with:
    - `"type": "followers"`.
    - `"followers"`: A list of serialized follower authors.
    - HTTP 404 if the specified author does not exist.

    Special Cases:
    - Handles both local and remote requests.
    - Ensures the author is not marked as deleted before retrieving followers.
    """

    try:
        author =  get_object_or_404(Author, serial=AUTHOR_SERIAL, is_deleted=False)
        followers = author.followers.all()

        authors = [follow.follower for follow in followers]
        serialized_followers = AuthorSerializer(authors, many=True)
        return Response({
            "type": "followers",
            "followers": serialized_followers.data
        })
    except Author.DoesNotExist:
        return Response({"detail": "Author not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET','PUT','DELETE'])
def foreign_followers(request, AUTHOR_SERIAL=None, FOREIGN_AUTHOR_FQID=None):
    """
    Handles operations on a foreign author as a follower of a local author.

    URL Pattern:
    - ://service/api/authors/{AUTHOR_SERIAL}/followers/{FOREIGN_AUTHOR_FQID}
    Example:
    - http://localhost:8000/api/authors/1/followers/http%3A%2F%2F127.0.0.1%3A8000%2Fapi%2Fauthors%2F3

    Behavior:
    1. **GET**:
    - Checks if the foreign author (`FOREIGN_AUTHOR_FQID`) is a confirmed follower of the local author (`AUTHOR_SERIAL`).
    - Returns serialized details of the foreign author if they are a confirmed follower (`pending='no`').
    - Returns HTTP 404 if the foreign author is not a follower.

    2. **PUT**:
    - Adds the foreign author as a confirmed follower of the local author.
    - If the follow request exists but is pending (`pending='yes'`), it updates the follow status to confirmed.
    - Requires the local author to be authenticated.

    3. **DELETE**:
    - Removes the foreign author as a follower of the local author.
    - Requires the local author to be authenticated.
    - Returns HTTP 404 if the foreign author is not a confirmed follower.

    Parameters:
    - AUTHOR_SERIAL: Numeric identifier for the local author.
    - FOREIGN_AUTHOR_FQID: Fully qualified identifier (percent-encoded URL) of the foreign author.

    Returns:
    - GET:
    - HTTP 200 with serialized foreign author details if they are a confirmed follower.
    - HTTP 404 if the foreign author is not a follower or the follow request is not confirmed.
    - PUT:
    - HTTP 201 with serialized foreign author details if the follow request is accepted.
    - HTTP 403 if the local author is not authenticated.
    - HTTP 404 if the foreign author is already a confirmed follower.
    - DELETE:
    - HTTP 200 with serialized foreign author details if the unfollow action is successful.
    - HTTP 403 if the local author is not authenticated.
    - HTTP 404 if the foreign author is not a confirmed follower.

    Special Cases:
    - The foreign author's FQID is decoded using `urllib.parse.unquote` to handle percent-encoded URLs.
    - Requires the requesting user to be authenticated as the local author for `PUT` and `DELETE` operations.
    """

    foreign_author_fqid = urllib.parse.unquote(FOREIGN_AUTHOR_FQID)
    foreign_author = get_object_or_404(Author, fqid=foreign_author_fqid, is_deleted=False)

    author =  get_object_or_404(Author, serial=AUTHOR_SERIAL, is_deleted=False)
    follow_objects = author.followers.all()
    follow_object = None
    for follow in follow_objects:
        if foreign_author.fqid == follow.follower.fqid:
            follow_object = follow
            
    if request.method == "GET":
        if follow_object and follow_object.pending == 'no':
                serializer = AuthorSerializer(foreign_author)
                return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"detail": f"You are not a follower of {AUTHOR_SERIAL}."}, status=status.HTTP_404_NOT_FOUND)
            
    elif request.method == "PUT":
        if request.user.author == author:
            if follow_object and follow_object.pending == 'yes':
                follow.accept()
                serializer = AuthorSerializer(foreign_author)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response({"detail": f"You are already a follower of {AUTHOR_SERIAL}."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"detail": f"Must be authenticated {AUTHOR_SERIAL}."}, status=status.HTTP_403_FORBIDDEN)
            
    elif request.method == "DELETE":
        if request.user.author == author:
            if follow_object and follow_object.pending == 'no':
                follow_object.delete()
                serializer = AuthorSerializer(foreign_author)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response({"detail": f"You are not a follower of {AUTHOR_SERIAL}."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"detail": f"Must be authenticated {AUTHOR_SERIAL}."}, status=status.HTTP_403_FORBIDDEN)
    
 
@api_view(['POST'])
def inbox(request, AUTHOR_SERIAL):
    """
    Handles operations on an author's inbox, allowing remote nodes to send various objects.

    URL Pattern:
    - ://service/api/authors/{AUTHOR_SERIAL}/inbox
    Example:
    - POST: Handles incoming objects (like, follow, comment, or post) for the author identified by `AUTHOR_SERIAL`.

    Behavior:
    1. **POST**:
    - Processes the object sent to the author's inbox based on the `type` field in the request body:
        - `like`: Handles a like object sent to the author.
        - `follow`: Handles a follow request sent to the author.
        - `comment`: Handles a comment object for one of the author's posts.
        - `post`: Handles a post shared to the author's inbox.
    - Delegates processing to specialized handlers based on the `type`.

    Parameters:
    - AUTHOR_SERIAL: Numeric identifier for the author.
    - Body: A JSON object containing the type and details of the object being sent.

    Returns:
    - HTTP 200 if the object is successfully processed.
    - HTTP 400 if:
    - The `type` field is missing or invalid.
    - An error occurs during object processing.
    - HTTP 404 if the author does not exist or is deleted.

    Special Cases:
    - Requires the `type` field in the request body to identify the object type.
    - Handles specific logic for:
    - Likes (`handle_like_inbox`).
    - Follows (`handle_follow_inbox`).
    - Comments (`handle_comment_inbox`).
    - Posts (`handle_post_inbox`).
    """

    author = get_object_or_404(Author, serial=AUTHOR_SERIAL, is_deleted=False)
    try: 
        type = request.data.get('type')
    except:
        return Response({"error": "Type is not found in the feild."}, status=status.HTTP_400_BAD_REQUEST)
    
    if type == 'like':
        return handle_like_inbox(request, author)
        
    elif type == 'follow':
        return handle_follow_inbox(request, author)

    elif type == 'comment':
        return handle_comment_inbox(request, author)
    
    elif type == 'post':
        return handle_post_inbox(request, author)
       
    return Response({"error": "Nothing matched with feild 'type'"},status=status.HTTP_400_BAD_REQUEST)

def handle_like_inbox(request, author):
    """
    Handles incoming like objects sent to an author's inbox.

    Parameters:
    - `request`: The incoming HTTP request containing the like data.
    - `author`: The target author to whom the like is being sent.

    Behavior:
    1. Validates the `object` field in the request data:
    - Ensures that the object being liked belongs to the specified author.
    - If invalid, returns HTTP 400 with an appropriate error message.
    2. Retrieves the `id` of the like (`like_fqid`) and the sender's details.
    - If the sender's author object does not already exist locally, it is created using `get_or_create_copy_author_object`.
    3. Logs the receipt of the like and validates the like object using the `LikeSerializer`:
    - If the data is valid:
        - Saves the like object, associating it with the sender and the `like_fqid`.
        - Returns HTTP 201 with the serialized like data.
    - If the data is invalid:
        - Returns HTTP 400 with validation error messages.

    Returns:
    - HTTP 201 with serialized like data if the like is successfully processed.
    - HTTP 400 if:
    - The `object` field is invalid or missing.
    - Validation of the like data fails.

    Special Cases:
    - Ensures that likes are only processed for objects owned by the target author.
    - Automatically creates a local copy of the sender's author object if it does not exist.
    """

    object = request.data.get("object")
    if not object and str(author.host) not in object:
        return Response({"error": f"object is not own by {author}."}, status=status.HTTP_400_BAD_REQUEST)
    
    like_fqid = request.data.get("id")
    sender = get_or_create_copy_author_object(request.data.get("author", {}))
    print(f"{author} received a like from {sender}")
    serializer = LikeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=sender, fqid=like_fqid)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

def handle_follow_inbox(request, author):
    """
    Handles incoming follow requests sent to an author's inbox.

    Parameters:
    - `request`: The incoming HTTP request containing the follow request data.
    - `author`: The target author to whom the follow request is being sent.

    Behavior:
    1. Extracts the actor's details from the request data and ensures their author object exists locally:
    - If not, creates a copy using `get_or_create_copy_author_object`.
    2. Checks the existing follow relationships:
    - `follow_exists`: If the actor is already following the target author.
    - `unapproved_follow_exists`: If a follow request from the actor is pending approval.
    - `mutual_follow`: If the target author is already following the actor.
    3. Responds based on the follow relationship status:
    - If the authors are mutual followers (`follow_exists` and `mutual_follow`), returns HTTP 200 with a message indicating they are already friends.
    - If the actor is already following the target author, returns HTTP 409 with a conflict message.
    - If a follow request is pending, returns HTTP 409 with a conflict message.
    4. If no existing follow relationship conflicts:
    - Creates a new `Follow` object with `pending='yes'`.
    - Constructs a response object containing:
        - Type: `"follow"`.
        - Summary: A description of the follow request.
        - Serialized actor and object author data.
    - Returns HTTP 201 with the response data.

    Returns:
    - HTTP 201 with follow request details if the follow request is successfully created.
    - HTTP 200 if the authors are already mutual followers.
    - HTTP 409 if:
    - The actor is already following the target author.
    - A follow request is already pending approval.

    Special Cases:
    - Automatically creates a local copy of the actor's author object if it does not exist.
    - Ensures follow relationships are appropriately managed, preventing duplicates or redundant requests.
    """

    object_author = author

    actor = get_or_create_copy_author_object(request.data.get("actor", {}))
    
    follow_exists = Follow.objects.filter(follower=actor, followed=object_author, pending='no').exists() # already follow request already exists
    unapproved_follow_exists = Follow.objects.filter(follower=actor, followed=object_author, pending='yes').exists() # not yet approved
    mutual_follow = Follow.objects.filter(follower=object_author, followed=actor, pending='no').exists() # object_author followed actor already
        
    if follow_exists and mutual_follow:
        return Response({"detail": "Authors are already friends."}, status=status.HTTP_200_OK)
    elif follow_exists:
        return Response({"detail": "Already following."}, status=status.HTTP_409_CONFLICT)
    elif unapproved_follow_exists:
        return Response({"detail": "Follow request already exists."}, status=status.HTTP_409_CONFLICT)    
    
    Follow.objects.create(follower=actor, followed=object_author, pending='yes')
    
    response_data = {
            "type": "follow",
            "summary": f"{actor.display_name} wants to follow {object_author.display_name}",
            "actor": AuthorSerializer(actor).data,
            "object": AuthorSerializer(object_author).data,
        }

    return Response(response_data, status=status.HTTP_201_CREATED)
    
def handle_comment_inbox(request, author):
    """
    Handles incoming comment objects sent to an author's inbox.

    Parameters:
    - `request`: The incoming HTTP request containing the comment data.
    - `author`: The target author to whom the comment is being sent.

    Behavior:
    1. Validates the `post` field in the request data:
    - Ensures that the post exists and is not marked as deleted (`is_deleted=False`).
    - If invalid, returns HTTP 400 with an appropriate error message.
    2. Retrieves the post associated with the comment.
    3. Ensures the comment's sender exists locally:
    - If not, creates a copy using `get_or_create_copy_author_object`.
    4. Checks if the comment already exists:
    - If the comment does not exist:
        - Validates and saves the comment using the `CommentSerializer`.
        - Associates the comment with the sender and its `fqid`.
        - Returns HTTP 201 with serialized comment data if successful.
    - If the comment already exists:
        - Updates the comment with the new data.
        - Returns HTTP 200 with serialized updated comment data.
    5. Handles validation and save errors:
    - Returns HTTP 400 for validation errors.
    - Returns HTTP 500 for unexpected errors.

    Returns:
    - HTTP 201 with serialized comment data if a new comment is successfully created.
    - HTTP 200 with serialized updated comment data if the comment already exists and is updated.
    - HTTP 400 if:
    - The `post` field is invalid or missing.
    - Validation of the comment data fails.
    - The post does not match the expected `AUTHOR_SERIAL`.
    - HTTP 500 if an unexpected error occurs during processing.

    Special Cases:
    - Automatically creates a local copy of the sender's author object if it does not exist.
    - Ensures that the associated post exists and is not marked as deleted before processing the comment.
    """

    # check if post exists
    post_fqid = request.data.get("post")
    print(request.data)
    post_exists = Post.objects.filter(fqid=post_fqid, is_deleted=False).exists()
    if not post_exists:
        return Response({"error": "post field is required."}, status=status.HTTP_400_BAD_REQUEST)
    post = get_object_or_404(Post, fqid=post_fqid, is_deleted=False)

    # create an author copy if author doesn't exists
    sender = get_or_create_copy_author_object(request.data.get("author", {}))
    
    print(f"{author} received a comment from {sender}")
    
    comment_fqid = request.data.get("id")
    comment_exists = Comment.objects.filter(fqid=comment_fqid, is_deleted=False).exists()
    
    if not comment_exists:
        try:
            serializer = CommentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(author=sender, fqid=comment_fqid)
                print(f"Comment copy created successfully: {sender.display_name} (fqid: {sender.fqid})")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # error handling
            else:
                print(f"Comment validation failed {serializer.errors}")
                return Response({'errors': f"Comment validation failed {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            print(f"Validation Error: {e.detail}")
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    else:
        print("Comment copy need updates")
    serializer = CommentSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(post=post, author=sender)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response({"error": "Post doesn't matched with AUTHOR_SERIAL"},status=status.HTTP_400_BAD_REQUEST)
 
def handle_post_inbox(request, author):
    """
    Handles incoming post objects sent to an author's inbox.

    Parameters:
    - `request`: The incoming HTTP request containing the post data.
    - `author`: The target author to whom the post is being sent.

    Behavior:
    1. Ensures the sender (author of the post) exists locally:
    - If not, creates a copy using `get_or_create_copy_author_object`.
    2. Checks if the post already exists based on its `fqid`:
    - If the post does not exist:
        - Validates and saves the post using the `PostSerializer`.
        - Associates the post with the sender and its `fqid`.
        - Returns HTTP 201 with serialized post data if successful.
    - If the post exists:
        - Updates the existing post with the new data.
        - Returns HTTP 200 with serialized updated post data.
    3. Handles validation and save errors:
    - Returns HTTP 400 for validation errors.
    - Returns HTTP 500 for unexpected errors during processing.

    Returns:
    - HTTP 201 with serialized post data if a new post is successfully created.
    - HTTP 200 with serialized updated post data if the post already exists and is updated.
    - HTTP 400 if validation of the post data fails.
    - HTTP 500 if an unexpected error occurs during processing.

    Special Cases:
    - Automatically creates a local copy of the sender's author object if it does not exist.
    - Ensures that the post exists and is not marked as deleted before attempting updates.
    """

    # create an author copy if author doesn't exists
    sender = get_or_create_copy_author_object(request.data.get("author", {}))
    
    print(f"{author} received a post from {sender}")
    post_fqid = request.data.get("id")
    post_exists = Post.objects.filter(fqid=post_fqid, is_deleted=False).exists()
    # create a post copy if post doesn't exists
    if not post_exists:
        try:
            serializer = PostSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(author=sender, fqid=post_fqid)
                print(f"Post copy created successfully: {sender.display_name} (fqid: {sender.fqid})")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                            
            # error handling
            else:
                print(f"Post validation failed {serializer.errors}")
                return Response({'errors': f"Post validation failed {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            print(f"Validation Error: {e.detail}")
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # update a post
    else:
        post = get_object_or_404(Post, fqid=post_fqid, is_deleted=False)
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print(f"Post copy updated successfully: {sender.display_name} (fqid: {sender.fqid})")
            return Response({"detail": f"Post already exists with fqid {post_fqid}.", "post": PostSerializer(post, context={'request': request}).data},
                            status=status.HTTP_200_OK,)
        else:
            print(f"Author validation failed {serializer.errors}")
            return Response({'errors': f"Author validation failed {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
    
def get_or_create_copy_author_object(author_data):
    """
    Retrieves or creates a local copy of an author object.

    Parameters:
    - `author_data`: A dictionary containing the data of the author. Must include the `id` (FQID) of the author.

    Behavior:
    1. Checks if an author with the specified `fqid` exists locally and is not marked as deleted (`is_deleted=False`).
    - If the author exists, retrieves and returns the existing `Author` object.
    2. If the author does not exist:
    - Validates the provided `author_data` using the `AuthorSerializer`.
    - Creates and saves a new local copy of the author.
    - Logs the successful creation of the author copy.
    - Returns the newly created `Author` object.
    3. Handles validation errors during the creation process:
    - Raises a `ValidationError` if the provided `author_data` is invalid.

    Returns:
    - The existing or newly created `Author` object.

    Raises:
    - `ValidationError`: If the provided `author_data` fails validation.

    Special Cases:
    - Ensures that only authors with valid and complete data are created locally.
    - Prevents duplication by checking the existence of an author before creating a new one.
    """

    fqid = author_data.get("id")
    
    if Author.objects.filter(fqid=fqid, is_deleted=False).exists():
        return get_object_or_404(Author, fqid=fqid, is_deleted=False)
    else:
        serializer = AuthorSerializer(data=author_data)
        if serializer.is_valid():
            author = serializer.save(fqid=fqid)
            print(f"Author copy created successfully: {author.display_name} (fqid: {author.fqid})")
            return author
        else:
            raise ValidationError(serializer.errors)
            



'''
The edit_profile function allows the user to edit their profile. The user must be logged in to edit their profile.
'''
def edit_profile(request, author_id):
    author = Author.objects.get(id=author_id)
    # From https://www.geeksforgeeks.org/fix-django-wsgirequest-object-has-no-attribute-data/
    # From https://www.freecodecamp.org/news/python-bytes-to-string-how-to-convert-a-bytestring/
    data = request.body.decode("utf-8")
    serializer = AuthorSerializer(author, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    # Return to ui
    return

