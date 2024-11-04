from django.shortcuts import render
from author.models import Author
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from post.serializers import PostSerializer, RepostSerializer
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from post.models import Post, Repost
from rest_framework import status, permissions
from rest_framework import permissions
from rest_framework.authentication import get_authorization_header
import base64
from django.http import HttpResponse

# Create your views here.

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
    
    # @action(detail=True, methods=['post'])
    # def share(self, request, pk=None):
    #     """
    #     Shares a public post. Creates a copy of the post attributed to the user sharing it.
    #     """
    #     try:
    #         original_post = self.get_object()  # Retrieve the original post by its primary key (pk) provided in the URL

    #         # Only allow sharing of public posts
    #         if original_post.visibility != 'public':
    #             # If the post is not public, respond with a 403 Forbidden status and a descriptive message
    #             return Response({"detail": "Only public posts can be shared."}, status=status.HTTP_403_FORBIDDEN)

    #         # Create a new post that represents the shared post
    #         shared_post = Post.objects.create(
    #             author=request.user.author,  # The user sharing the post becomes the author of the new shared post
    #             title=f"Shared: {original_post.title}",  # Prefix "Shared: " to the original post title
    #             content=original_post.content,  # Copy content from the original post
    #             content_type=original_post.content_type,  # Keep the same content type (e.g., text, image)
    #             image_content=original_post.image_content,  # Copy the image content if available
    #             visibility="public",  # The shared post is set to public visibility by default
    #         )

    #         # Serialize the newly created shared post to prepare it for the response
    #         serializer = self.get_serializer(shared_post)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)  # Send back the shared post data with a 201 Created status

    #     except Post.DoesNotExist:
    #         # If the original post does not exist, return a 404 Not Found response with a descriptive message
    #         return Response({"detail": "Original post not found."}, status=status.HTTP_404_NOT_FOUND)

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
        reposts = Repost.objects.all()
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


class RepostView(ModelViewSet):
    queryset = Repost.objects
    serializer_class = RepostSerializer
    
    def create(self, request, *args, **kwargs):
        data = request.data
        print(data)
        post = data.get('post')
        reposted_by_id = data.get('reposted_by')
        
        if not post or not reposted_by_id:
            return Response({"error": "Post and reposted_by fields are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the post exists
        try:
            original_post = Post.objects.get(id=post)
        except Post.DoesNotExist:
            return Response({"error": "Post does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        try:
            reposted_by = Author.objects.get(id=reposted_by_id)
        except Author.DoesNotExist:
            return Response({"error": "Author does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        repost = Repost.objects.filter(post=original_post, reposted_by=reposted_by).first()
        
        if repost:
            repost.delete()
            return Response({"message": "Repost removed"}, status=status.HTTP_204_NO_CONTENT)
        else:
            repost = Repost(post=original_post, reposted_by=reposted_by)
            repost.save()
            serializer = self.get_serializer(repost)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    def get_queryset(self):
        queryset = super().get_queryset()
        original_post_id = self.request.query_params.get('post')
        reposted_by_id = self.request.query_params.get('reposted_by')
        
        if original_post_id:
            queryset = queryset.filter(post=original_post_id)
        
        if reposted_by_id:
            queryset = queryset.filter(reposted_by=reposted_by_id)
            
        return queryset.order_by("created_at")
    
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     current_user = self.request.user

    #     # Filter for not deleted posts
    #     queryset = queryset.filter(is_deleted=False)
        
    #     author_id = self.request.query_params.get('author_id')
    #     visibility = self.request.query_params.get("visibility")
    #     title = self.request.query_params.get('title')
    #     following_list = self.request.query_params.get("following_list")

    #     if author_id and visibility:
    #         queryset = queryset.filter(visibility="public", author__id=author_id)
    #     elif title:
    #         queryset = queryset.filter(title=title)
    #     elif following_list:
    #         current_author = Author.objects.get(user=current_user)
    #         followed_by_user = Author.objects.filter(followers__follower=current_author)
    #         queryset = queryset.filter(author__id__in=followed_by_user)

    #     # Include 'friend-only' posts if the viewer is a friend of the author
    #     if current_user.is_authenticated:
    #         current_author = Author.objects.get(user=current_user)
    #         friend_ids = Author.objects.filter(followers__follower=current_author, following__followed=current_author, following__pending="no").values_list('id', flat=True)
    #         queryset = queryset.filter(visibility__in=["public", "unlisted"]).union(
    #             queryset.filter(visibility="friend-only", author__id__in=friend_ids)
    #         )

    #     return queryset.order_by("updated_at")

        

            
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     current_user = self.request.user

    #     # Only include non-deleted reposts
    #     queryset = queryset.filter(is_deleted=False)

    #     # Fetch query parameters
    #     author_id = self.request.query_params.get('author_id')
    #     title = self.request.query_params.get('title')
    #     following_list = self.request.query_params.get("following_list")
        
    #     original_post_id = self.request.query_params.get('post')
    #     reposted_by_id = self.request.query_params.get('reposted_by')
        
    #     if original_post_id:
    #         queryset = queryset.filter(post=original_post_id)
        
    #     if reposted_by_id:
    #         queryset = queryset.filter(reposted_by=reposted_by_id)

    #     # Filter for reposts by specific author
    #     if author_id:
    #         queryset = queryset.filter(reposted_by__id=author_id)
    #     elif title:
    #         queryset = queryset.filter(post__title=title)
    #     elif following_list:
    #         current_author = Author.objects.get(user=current_user)
    #         followed_by_user = Author.objects.filter(following=current_author)
    #         queryset = queryset.filter(reposted_by__id__in=followed_by_user.values_list('id', flat=True))

    #     # Additional filtering for friend-only reposts visible to mutual friends
    #     if current_user.is_authenticated:
    #         current_author = Author.objects.get(user=current_user)
    #         friend_ids = Author.objects.filter(
    #             followers=current_author,
    #             following=current_author
    #         ).values_list('id', flat=True)

    #         # Filter for public, unlisted, and friend-only reposts from friends
    #         queryset = queryset.filter(reposted_by__id__in=friend_ids)

    #     return queryset.order_by("created_at")
