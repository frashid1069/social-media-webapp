from django.shortcuts import render
from author.serializers import AuthorSerializer, Author
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from post.serializers import PostSerializer
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from post.models import Post
from rest_framework import status, permissions
from rest_framework import permissions
from rest_framework.authentication import get_authorization_header
import base64
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from service.utils.push import push
from service.utils.check_friend import check_friend

class PostPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'size'
    page_query_param = 'page'  
    
    # sorting
    def paginate_queryset(self, queryset, request, view=None):
        if not queryset.ordered:
            queryset = queryset.order_by('updated_at')
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
    #authentication_classes = [authentication.JwtQueryParamsAuthentication]
    #authentication_classes = []
    # queryset = Post.objects
    # queryset = Post.objects.all()
    queryset = Post.objects.select_related('author').all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]  # Allows public access for reading

    
    
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

        # Restrict friend-only posts to friends
        elif post.visibility == 'friend-only':
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
def post_detail(request, POST_SERIAL=None, AUTHOR_SERIAL=None, POST_FQID=None):
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}
    eg. http://localhost:8000/api/authors/1/posts/1
        GET [local, remote] get the public post whose serial is POST_SERIAL
            friends-only posts: must be authenticated
        DELETE [local] remove a
            local posts: must be authenticated locally as the author
        PUT [local] update a post
            local posts: must be authenticated locally as the author
    """
    
    if POST_SERIAL is not None and AUTHOR_SERIAL is not None:
        author = get_object_or_404(Author, serial=AUTHOR_SERIAL)
        post = get_object_or_404(Post, serial=POST_SERIAL, author=author.serial)
    elif POST_FQID is not None:
        post = get_object_or_404(Post, fqid=POST_FQID)
    else:
        return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
    
    
    if request.method == 'GET':
        serializer = PostSerializer(post)
        if serializer.data.get("visibility") == "friends-only":
            if check_friend(author, request.user.author) or request.user.author == author:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "You are not authorized to get this post."}, status=status.HTTP_403_FORBIDDEN)
               
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        if request.user.author.serial != AUTHOR_SERIAL:
            return Response({"detail": "You are not authorized to update this post."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if request.user.author.serial != AUTHOR_SERIAL:
            return Response({"detail": "You are not authorized to delete this post."}, status=status.HTTP_403_FORBIDDEN)

        # soft delete the post
        post.is_deleted = True
        post.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST', 'GET'])
def post_list(request, AUTHOR_SERIAL):
    """
    URL ://service/api/authors/{AUTHOR_SERIAL}/posts/
    eg. http://localhost:8000/api/authors/1/posts/
    eg. http://localhost:8000/api/authors/3/posts/?page=1&size=1
        GET [local, remote] get the recent posts from author AUTHOR_SERIAL (paginated)
            Not authenticated: only public posts.
            Authenticated locally as author: all posts.
            Authenticated locally as friend of author: public + friends-only posts.
            Authenticated as remote node: This probably should not happen. Remember, the way remote node becomes aware of local posts is by local node pushing those posts to inbox, not by remote node pulling.
        POST [local] create a new post but generate a new ID
            Authenticated locally as author
    """
    author = get_object_or_404(Author, serial=AUTHOR_SERIAL)
    
    if request.method == 'GET':
        if request.user.author == author:
            posts = Post.objects.filter(author=author)
        elif check_friend(request.user.author, author):
            posts = Post.objects.filter(author=author).filter(visibility__in=['public', 'friends-only'])
        else:
            posts = Post.objects.filter(author=author, visibility='public')
             
        # TODO: to_representation and to_internal_value
     
        paginator = PostPagination()
        paged_posts = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(paged_posts, many=True)
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

            serializer = PostSerializer(data=request_data)
        else:   
            serializer = PostSerializer(data=request.data)
            
        if serializer.is_valid():
            serializer.save(author=author)
            # push to inbox
            push(author, request, serializer.data)
           
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET'])    
def post_image(request, POST_SERIAL=None, AUTHOR_SERIAL=None, POST_FQID=None):
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/image
    eg. http://127.0.0.1:8000/api/authors/3/posts/7/image
        GET [local, remote] get the public post converted to binary as an image
        return 404 if not an image
    URL: ://service/api/posts/{POST_FQID}/image
    eg. http://127.0.0.1:8000/api/posts/http://127.0.0.1:8000/api/authors/3/posts/7/image
        GET [local, remote] get the public post converted to binary as an image
        return 404 if not an image
    """
    if POST_SERIAL is not None and AUTHOR_SERIAL is not None:
        image_post = get_object_or_404(Post, author=AUTHOR_SERIAL, serial=POST_SERIAL)
        # if 'image/png;base64' != post.content_type or 'image/jpeg;base64' not in post.content_type
        if 'image/png' == image_post.content_type or 'image/jpeg' == image_post.content_type:
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
    URL ://service/api/posts/
    """
    
    author = request.user.author
    follow_objects = author.following.filter(pending='no')
    posts = Post.objects.filter(visibility='public') # all public
    posts = posts | Post.objects.filter(author=author) # all mine
    
    if follow_objects: 
        for follow in follow_objects:
            if follow.pending == 'no':

                if check_friend(follow.followed, author):
                    posts = posts | Post.objects.filter(author=follow.followed, visibility__in=['unlisted', 'friends-only'])
                else:
                    posts = posts | Post.objects.filter(author=follow.followed, visibility='unlisted')
     
    posts = posts.order_by("-updated_at")
    serializer = PostSerializer(posts, many=True)
    response_data = {
            "type":"posts",
            "count": len(serializer.data),
            "src": serializer.data
        }
    return Response(response_data, status=status.HTTP_200_OK)