from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from post.serializers import PostSerializer
from rest_framework.viewsets import ModelViewSet
from post.models import Post
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response

# Create your views here.

class PostView(ModelViewSet):
    #authentication_classes = [authentication.JwtQueryParamsAuthentication]
    #authentication_classes = []
    queryset = Post.objects
    serializer_class = PostSerializer
    
    
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
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="Retrieve a single post",
        description="Fetch the details of a post by its ID.",
        responses={200:  PostSerializer, 404: "Not Found"},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
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
        Shares a public post. Creates a copy of the post attributed to the user sharing it.
        """
        try:
            original_post = self.get_object()

            # Only allow sharing of public posts
            if original_post.visibility != 'public':
                return Response({"detail": "Only public posts can be shared."}, status=status.HTTP_403_FORBIDDEN)

            # Create a new post for the share
            shared_post = Post.objects.create(
                author=request.user.author,  # Set to the current user
                title=f"Shared: {original_post.title}",
                content=original_post.content,
                content_type=original_post.content_type,
                image_content=original_post.image_content,
                visibility="public",  # Shared posts are public
            )

            serializer = self.get_serializer(shared_post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Post.DoesNotExist:
            return Response({"detail": "Original post not found."}, status=status.HTTP_404_NOT_FOUND)