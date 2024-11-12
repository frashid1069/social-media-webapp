from django.shortcuts import render, get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.viewsets import ModelViewSet
from comment.models import Comment
from comment.serializer import CommentSerializer
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from author.serializers import Author, AuthorSerializer
from post.serializers import Post

class CommentView(ModelViewSet):
    queryset = Comment.objects
    serializer_class = CommentSerializer
    
    @extend_schema(
        summary="Retrieve a list of comments",
        description="""
        Retrieve a list of comments, with optional filtering. 
        - If `post_id` is provided, only comments for that post will be returned.
        """,
        parameters=[
            OpenApiParameter(name="post_id", description="Filter comments by the post's ID", required=False, type=OpenApiTypes.INT),
        ],
        responses={200: CommentSerializer(many=True), 400: "Bad Request"},
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
        request=CommentSerializer,
        responses={201: CommentSerializer, 400: "Bad Request"},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a single comment",
        description="Fetch the details of a specific comment by its ID.",
        responses={200: CommentSerializer, 404: "Not Found"},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update an existing comment",
        description="Update the content of an existing comment.",
        request=CommentSerializer,
        responses={200: CommentSerializer, 400: "Bad Request", 404: "Not Found"},
    )
    def update(self, request, *args, **kwargs):
        author = self.get_object()
        if author.user != request.user:
            raise PermissionDenied("You do not have permission to edit this profile.")
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a comment",
        description="Delete a comment by its ID.",
        responses={204: None, 404: "Not Found"},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
# Comments API
@api_view(['POST'])
def create_comment(request, author_id):
    '''
    authors/<int:author_id>/inbox
    '''
    author = get_object_or_404(Author, id=author_id)
    
    if not request.user.is_authenticated:
        return Response({"detail": "You are not authorized to create a comment for this post."}, status=status.HTTP_403_FORBIDDEN)
         
    serializer = CommentSerializer(data=request.data)
        
    if serializer.is_valid():
        serializer.save(author=author)
        comment = serializer.data
        
        response_data = {
                "type": "comment",
                "author": AuthorSerializer(author).data,
                "comment": comment['content'],
                "contentType": "text/markdown",
                "published": comment['created_at'],
                "id": "http://nodeaaaa/api/authors/111/commented/130",
                "post": "http://nodebbbb/api/authors/222/posts/249",
                "likes": "likes",        
            }
        return Response(response_data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET'])    
def comment_list(request, post_id, author_id):
    '''
    authors/<int:author_id>/posts/<int:post_id>/comments
    '''
    post = get_object_or_404(Post, id=post_id)
    author = get_object_or_404(Author, id=author_id)
    response_data = {
                "type":"comments",
                "page":"http://nodebbbb/authors/222/posts/249",
                "id":"http://nodebbbb/api/authors/222/posts/249/comments",
                "page_number":1,
                "size":5,
                "count": 1023,
                "src": "comments"
            }     

@api_view(['GET'])    
def comment_list_fqid(request, fqid):
    post = get_object_or_404(Post, id=fqid)
    response_data = {
                "type":"comments",
                "page":"http://nodebbbb/authors/222/posts/249",
                "id":"http://nodebbbb/api/authors/222/posts/249/comments",
                "page_number":1,
                "size":5,
                "count": 1023,
                "src": "comments"
            }     
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])    
def comment_detail(request, author_id, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    response_data = {
                "type":"comments",
                "page":"http://nodebbbb/authors/222/posts/249",
                "id":"http://nodebbbb/api/authors/222/posts/249/comments",
                "page_number":1,
                "size":5,
                "count": 1023,
                "src": "comments"
            }     
    return Response(response_data, status=status.HTTP_200_OK)

# Commented API
@api_view(['GET'])    
def author_comment_list(request, author_id):
    author = get_object_or_404(Post, id=author_id)
    response_data = {
                "type":"comments",
                "page":"http://nodebbbb/authors/222/posts/249",
                "id":"http://nodebbbb/api/authors/222/posts/249/comments",
                "page_number":1,
                "size":5,
                "count": 1023,
                "src": "comments"
            }     
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])    
def author_comment_list_fqid(request, author_id,):
    author = get_object_or_404(Post, id=author_id)
    response_data = {
                "type":"comments",
                "page":"http://nodebbbb/authors/222/posts/249",
                "id":"http://nodebbbb/api/authors/222/posts/249/comments",
                "page_number":1,
                "size":5,
                "count": 1023,
                "src": "comments"
            }     
    return Response(response_data, status=status.HTTP_200_OK)