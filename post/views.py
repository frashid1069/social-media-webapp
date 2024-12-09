from django.shortcuts import render, get_object_or_404
from author.serializers import AuthorSerializer, Author
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from post.serializers import PostSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from post.models import Post
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authentication import get_authorization_header
import base64
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from service.utils.push import push
from service.utils.check_friend import check_friend
from rest_framework.exceptions import PermissionDenied, ValidationError



class PostPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'size'
    page_query_param = 'page'  
    
    # sorting
    def paginate_queryset(self, queryset, request, view=None):
        if not queryset.ordered:
            queryset = queryset.order_by('updated_at').filter(is_deleted=False)
        return super().paginate_queryset(queryset, request, view=view)
    
    def get_paginated_response(self, data, count):
        response_data = {
                "type":"posts",
                "page_number":self.page.number,
                "size": self.get_page_size(self.request),
                "count": count,
                "src": data
            }     
        return Response(response_data, status=status.HTTP_200_OK)


class PostView(ModelViewSet):
    queryset = Post.objects.select_related('author').all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]  # Allows public access for reading

    
    
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
            OpenApiParameter(name="visibility", description="Filter posts by visibility (public, friends, unlisted)", required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name="title", description="Filter posts by title", required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name="following_list", description="Return posts from authors that the user follows", required=False, type=OpenApiTypes.BOOL),
        ],
        responses={200: PostSerializer(many=True), 400: "Bad Request"},
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
                current_author = Author.objects.get(user=current_user)
            else:
                current_author = Author.objects.get(id=author_id)
            print(current_author)
            followed_by_user = Author.objects.filter(followers__follower=current_author)
            print(followed_by_user)
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
        request= PostSerializer,
        responses={201:  PostSerializer, 400: "Bad Request"},
    )
    def create(self, request, *args, **kwargs):
        '''
        Handle image upload, encode the image file to base64 data
        '''
        content_type = request.data.get('content_type')
        print(content_type)
        if content_type == 'image/jpeg':
        
            image_file = request.FILES.get('content')
            if not image_file:
                return Response({"error": "An image file is required."},
                                status=status.HTTP_400_BAD_REQUEST)            
            # base64 encode
            image_data = image_file.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
            
            # request.data is immutable
            modified_data = request.data.copy()  
            modified_data['content'] = base64_data 
            serializer = self.get_serializer(data=modified_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
        
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return super().create(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        post = self.get_object()
        current_user = request.user

        # Allow access for public or unlisted posts
        if post.visibility in ['public', 'unlisted']:
            serializer = self.get_serializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Restrict friends posts to friends
        elif post.visibility == 'friends':
            # Retrieve the current author's profile based on the current user
            try:
                author = Author.objects.get(user=current_user)
            except Author.DoesNotExist:
                return Response({"detail": "Author not found"}, status=status.HTTP_404_NOT_FOUND)

            post_author = post.author

            # Check if the current user and the post author are mutual followers (friends)
            if author.is_friend_with(post_author):
                serializer = self.get_serializer(post)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "You do not have permission to view this post."}, status=status.HTTP_403_FORBIDDEN)

        # If none of the conditions are met, return 404
        return Response({"detail": "Post not found or access not allowed."}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Update an existing post",
        description="Update the title, content, or image of an existing post.",
        request= PostSerializer,
        responses={200:  PostSerializer, 400: "Bad Request", 404: "Not Found"},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """
        Share a post if its visibility is 'public'.
        """
        try:
            original_post = self.get_object()

            # Restrict sharing to public posts only
            if original_post.visibility != 'public':
                return Response({"detail": "Only public posts can be shared."}, status=status.HTTP_403_FORBIDDEN)

            # Proceed with sharing for public posts
            shared_post = Post.objects.create(
                author=request.user.author,
                title=f"Shared: {original_post.title}",
                content=original_post.content,
                content_type=original_post.content_type,
                image_content=original_post.image_content,
                visibility="public",  # Shared posts are public by default
            )
            serializer = self.get_serializer(shared_post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Post.DoesNotExist:
            return Response({"detail": "Original post not found."}, status=status.HTTP_404_NOT_FOUND)
    
    def list(self, request, *args, **kwargs):
        posts = Post.objects.all()
        return super().list(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], url_path='image', url_name='get_image')
    def get_image(self, request):
        '''
        ~api/image_post/image/?author_id=<pk>&post_id=<pk>
        Retrieve the decoded image based on author_id and image_id
        content_type (e.g. image/jpeg)
        '''
        author_id = request.query_params.get('author_id')
        post_id = request.query_params.get('post_id')
        
        image_post = get_object_or_404(Post, author=author_id, id=post_id)
        
        image_binary = base64.b64decode(image_post.content)
        content_type = image_post.content_type

        return HttpResponse(image_binary, content_type=content_type)

    

@api_view(['GET', 'PUT', 'DELETE'])
def post_detail(request, POST_SERIAL=None, AUTHOR_SERIAL=None):
    """
    Handles detailed operations on a specific post.

    URL Pattern:
    - ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}
    Example:
    - http://localhost:8000/api/authors/1/posts/1

    Behavior:
    1. **GET** [local, remote]:
    - Retrieves the details of the post identified by `POST_SERIAL` for the author identified by `AUTHOR_SERIAL`.
    - If the post visibility is set to "friends," the user must either be a friend of the author or the author themselves.
    - Returns the serialized post data.

    2. **PUT** [local]:
    - Updates a post identified by `POST_SERIAL` for the author identified by `AUTHOR_SERIAL`.
    - Only the authenticated author of the post can update it.
    - Handles updates, including handling image content by encoding it in base64.

    3. **DELETE** [local]:
    - Performs a soft delete on a post identified by `POST_SERIAL` for the author identified by `AUTHOR_SERIAL`.
    - Only the authenticated author of the post can delete it.
    - Sets the post visibility to "deleted" and marks it as deleted.

    Parameters:
    - AUTHOR_SERIAL: Numeric identifier for the author.
    - POST_SERIAL: Numeric identifier for the post.

    Returns:
    - GET:
    - HTTP 200 with serialized post data if successful.
    - HTTP 403 if the user is unauthorized to access the post.
    - HTTP 404 if the post is not found or already deleted.
    - PUT:
    - HTTP 200 with serialized updated post data if successful.
    - HTTP 403 if the user is unauthorized to update the post.
    - HTTP 400 for validation errors.
    - HTTP 500 for unexpected errors during save.
    - DELETE:
    - HTTP 204 if the post is successfully deleted.
    - HTTP 403 if the user is unauthorized to delete the post.
    - HTTP 400 if the post deletion fails.

    Special Cases:
    - If the post visibility is "friends," the `check_friend` function verifies access rights for the requesting user.
    - Handles image uploads by converting image content to base64 format for storage.
    """
    if POST_SERIAL is not None and AUTHOR_SERIAL is not None:
        author = get_object_or_404(Author, serial=AUTHOR_SERIAL)
        post = get_object_or_404(Post, serial=POST_SERIAL, author=author.id)
    else:
        return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
    
    if post.is_deleted == True:
        return Response({"detail": "This post is already deleted."}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
       
        
        serializer = PostSerializer(post, context={'request': request})
        if serializer.data.get("visibility") == "friends":
            if check_friend(author, request.user.author) or request.user.author == author:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "You are not authorized to get this post."}, status=status.HTTP_403_FORBIDDEN)

            
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        if request.user.author.serial != AUTHOR_SERIAL:
            return Response({"detail": "You are not authorized to update this post."}, status=status.HTTP_403_FORBIDDEN)
        
        # handle image post
        image_file = request.FILES.get('content')
        if image_file and image_file.content_type == 'image/jpeg':
            if not image_file:
                return Response({"error": "An image file is required."},
                                status=status.HTTP_400_BAD_REQUEST)            
            # base64 encode
            image_data = image_file.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
            
            # request.data is immutable
            request_data = request.data.copy()
            request_data['content'] = base64_data

            serializer = PostSerializer(post, data=request_data,  partial=True, context={'request': request})
        else:
            serializer = PostSerializer(post, data=request.data, partial=True, context={'request': request})
        print(request.data)
        try:
            if serializer.is_valid():
                serializer.save()  
                push(author, request, serializer.data)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            print(f"Validation Error: {e.detail}")
            return Response({"error": e.detail},  status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"detail": f"An error occurred while saving the post: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,)

        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if request.user.author.serial != AUTHOR_SERIAL:
            return Response({"detail": "You are not authorized to delete this post."}, status=status.HTTP_403_FORBIDDEN)

        # soft delete the post
        post.visibility = 'deleted'
        post.save()
        serializer = PostSerializer(post, context={'request': request})
        print(serializer.data)
        push(author, request, serializer.data)
        if post.visibility == 'deleted' and post.is_deleted == True:
            return Response({"detail": "Post is deleted"},status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Failed to delete"},status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def fqid_post_detail(request, POST_FQID=None):
    """
    Retrieves the details of a specific post using its fully qualified identifier (FQID).

    URL Pattern:
    - ://service/api/posts/{POST_FQID}
    Example:
    - GET [local]: Retrieves the public post identified by `POST_FQID`.

    Behavior:
    - Fetches the post identified by its FQID.
    - If the post's visibility is set to "friends," access is restricted:
    - The requesting user must be authenticated and either a friend of the author or the author themselves.
    - Returns the serialized post data.

    Parameters:
    - POST_FQID: Fully qualified identifier for the post.

    Returns:
    - HTTP 200 with serialized post data if successful.
    - HTTP 403 if the user is unauthorized to access the post.
    - HTTP 404 if the post is not found or is already deleted.

    Special Cases:
    - Ensures that deleted posts (`is_deleted=True`) are not accessible.
    - Visibility checks are performed using the `check_friend` function for posts restricted to "friends."
    """
    if POST_FQID is None:
        return Response({"detail": "Post not found with POST_FQID."}, status=status.HTTP_404_NOT_FOUND)
    
    post = get_object_or_404(Post, fqid=POST_FQID)
    if post.is_deleted == True:
        return Response({"detail": "This post is already deleted."}, status=status.HTTP_404_NOT_FOUND)
        
    
    serializer = PostSerializer(post, context={'request': request})
    if serializer.data.get("visibility") == "friends":
        author = post.author
        if check_friend(author, request.user.author) or request.user.author == author:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "You are not authorized to get this post."}, status=status.HTTP_403_FORBIDDEN)
        
    return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
@api_view(['POST', 'GET'])
def post_list(request, AUTHOR_SERIAL):
    """
    Handles retrieval and creation of posts for a specific author.

    URL Pattern:
    - ://service/api/authors/{AUTHOR_SERIAL}/posts/
    Example:
    - GET [local, remote]: Retrieves recent posts from the author identified by `AUTHOR_SERIAL` (paginated).
        - Not authenticated: Retrieves only public posts.
        - Authenticated locally as the author: Retrieves all posts.
        - Authenticated locally as a friend of the author: Retrieves public and "friends" posts.
        - Authenticated as a remote node: This scenario should not occur, as remote nodes become aware of posts through inbox pushes, not pulls.
    - POST [local]: Creates a new post for the author identified by `AUTHOR_SERIAL`.

    Behavior:
    1. **GET**:
    - Retrieves a paginated list of posts based on the authentication and relationship of the requesting user with the author.
    - Posts visibility rules:
        - Public posts: Accessible to all users.
        - "Friends" posts: Accessible to authenticated friends or the author themselves.
        - Private posts: Accessible only to the author.

    2. **POST**:
    - Allows the authenticated author to create a new post.
    - Supports handling of image content, which is base64 encoded before saving.
    - The new post is pushed to the appropriate inbox.

    Parameters:
    - AUTHOR_SERIAL: Numeric identifier for the author.

    Returns:
    - GET:
    - HTTP 200 with paginated serialized posts if successful.
    - Pagination includes a count of the returned posts.
    - POST:
    - HTTP 201 with serialized post data if successful.
    - HTTP 403 if the user is unauthorized to create a post for the author.
    - HTTP 400 for validation errors.

    Special Cases:
    - Image posts: Image content is base64 encoded before saving.
    - Friends-only posts: Access is determined using the `check_friend` function.
    - Push notifications: Created posts are pushed to the author's inbox.
    """

    author = get_object_or_404(Author, serial=AUTHOR_SERIAL)
    
    if request.method == 'GET':
        current_author = getattr(request.user, 'author', None)
        if current_author == author:
            posts = Post.objects.filter(author=author)
        elif check_friend(current_author, author):
            posts = Post.objects.filter(author=author).filter(visibility__in=['public', 'friends'])
        else:
            posts = Post.objects.filter(author=author, visibility='public')
        
        paginator = PostPagination()
        paged_posts = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(paged_posts, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data,len(serializer.data)) 
        

    elif request.method == 'POST':
        if not request.user.is_authenticated or request.user.author.serial != AUTHOR_SERIAL:
            return Response({"detail": "You are not authorized to create a post for this author."}, status=status.HTTP_403_FORBIDDEN)

        # handle image post
        image_file = request.FILES.get('content')
        if image_file and image_file.content_type == 'image/jpeg':
            if not image_file:
                return Response({"error": "An image file is required."},
                                status=status.HTTP_400_BAD_REQUEST)            
            # base64 encode
            image_data = image_file.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
            
            # request.data is immutable
            request_data = request.data.copy()
            request_data['content'] = base64_data

            # serializer = PostSerializer(data=request_data)
            serializer = PostSerializer(data=request_data, context={'request': request})
        else:   
            # serializer = PostSerializer(data=request.data)
            serializer = PostSerializer(data=request.data, context={'request': request})
            
        if serializer.is_valid():
            serializer.save(author=author)
            # push to inbox
            push(author, request, serializer.data)
            print(serializer.data)
           
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET'])
@permission_classes([AllowAny])
def post_image(request, POST_SERIAL=None, AUTHOR_SERIAL=None, POST_FQID=None):
    """
    Retrieves a post's content as an image in binary format.

    URL Patterns:
    1. ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/image
    Example:
    - http://127.0.0.1:8000/api/authors/3/posts/7/image
    - GET [local, remote]: Retrieves the image content of the post identified by `POST_SERIAL` for the author identified by `AUTHOR_SERIAL`.
    - Returns HTTP 404 if the post's content is not an image.

    2. ://service/api/posts/{POST_FQID}/image
    Example:
    - http://127.0.0.1:8000/api/posts/http://127.0.0.1:8000/api/authors/3/posts/7/image
    - GET [local, remote]: Retrieves the image content of the post identified by `POST_FQID`.
    - Returns HTTP 404 if the post's content is not an image.

    Behavior:
    - Converts the base64-encoded content of a post to binary and returns it as an image.
    - Verifies that the post's content type is either `image/png` or `image/jpeg`.
    - Handles retrieval for both `AUTHOR_SERIAL/POST_SERIAL` and `POST_FQID` formats.

    Parameters:
    - AUTHOR_SERIAL: Numeric identifier for the author.
    - POST_SERIAL: Numeric identifier for the post.
    - POST_FQID: Fully qualified identifier for the post.

    Returns:
    - HTTP 200 with the binary image data if successful.
    - HTTP 404 if the post or its image content is not found.
    - HTTP 404 if the post's content type is not an image (e.g., `image/png` or `image/jpeg`).

    Special Cases:
    - Base64-encoded content is decoded into binary format before returning.
    - Content type is verified to ensure only image formats are supported.
    """

    if POST_SERIAL is not None and AUTHOR_SERIAL is not None:
        author = get_object_or_404(Author, serial=AUTHOR_SERIAL)
        image_post = get_object_or_404(Post, author=author.id, serial=POST_SERIAL)
        # if 'image/png;base64' != post.content_type or 'image/jpeg;base64' not in post.content_type
        if 'image/png;base64' == image_post.content_type or 'image/jpeg;base64' == image_post.content_type:
            image_binary = base64.b64decode(image_post.content)
            content_type = image_post.content_type
            return HttpResponse(image_binary, content_type=content_type)
        
        return Response({"detail": "Image not found with AUTHOR_SERIAL/POST_SERIAL."}, status=status.HTTP_404_NOT_FOUND)
    
    elif POST_FQID is not None:
        
        image_post = get_object_or_404(Post, fqid=POST_FQID)
        if 'image/png' == image_post.content_type or 'image/jpeg' == image_post.content_type:
            image_binary = base64.b64decode(image_post.content)
            content_type = image_post.content_type
            return HttpResponse(image_binary, content_type=content_type)
        
        return Response({"detail": "Image not found with POST_FQID."}, status=status.HTTP_404_NOT_FOUND)

    else:
        return Response({"detail": "Image not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])        
def get_all_visible_post(request):
    """
    Retrieves all posts visible to the authenticated user.

    URL Pattern:
    - ://service/api/posts/
    Example:
    - GET: Retrieves all visible posts based on the user's authentication and relationships.

    Behavior:
    - Retrieves posts visible to the authenticated user, including:
    - All public posts (`visibility='public'`).
    - Posts authored by the authenticated user.
    - Posts from followed authors:
        - If the followed author is a friend, includes posts with visibility `unlisted` and `friends`.
        - Otherwise, includes posts with visibility `unlisted`.

    - Filters out deleted posts (`is_deleted=False`) and orders the posts by the latest updates.

    Parameters:
    - None (uses the authenticated user from the request).

    Returns:
    - HTTP 200 with a serialized list of visible posts:
    - "type": Always set to "posts".
    - "count": Total number of visible posts.
    - "src": Serialized post data.

    Special Cases:
    - Handles posts with visibility settings (`public`, `friends`, `unlisted`) based on the user's relationships.
    - Posts are ordered by the `updated_at` timestamp in descending order.
    """

    
    author = request.user.author
    follow_objects = author.following.filter(pending='no')
    posts = Post.objects.filter(visibility='public') # all public
    posts = posts | Post.objects.filter(author=author) # all mine
    
    if follow_objects: 
        for follow in follow_objects:
            if follow.pending == 'no':

                if check_friend(follow.followed, author):
                    posts = posts | Post.objects.filter(author=follow.followed, visibility__in=['unlisted', 'friends'])
                else:
                    posts = posts | Post.objects.filter(author=follow.followed, visibility='unlisted')
    
     
    posts = posts.filter(is_deleted=False, visibility__in=['unlisted', 'friends', 'public']).order_by("-updated_at")
    serializer = PostSerializer(posts, many=True, context={'request': request})
    response_data = {
            "type":"posts",
            "count": len(serializer.data),
            "src": serializer.data
        }
    return Response(response_data, status=status.HTTP_200_OK)