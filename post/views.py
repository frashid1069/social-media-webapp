from django.shortcuts import render
from author.models import Author
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from post.serializers import PostSerializer, RepostSerializer
from rest_framework.viewsets import ModelViewSet

from rest_framework.decorators import action
from rest_framework.response import Response
from post.models import Post, Repost
from rest_framework import status, permissions

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
    def list(self, request, *args, **kwargs):
        posts = Post.objects.all()
        reposts = Repost.objects.all()
        return super().list(request, *args, **kwargs)
    


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
    
        
    
    



        
