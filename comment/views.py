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
from rest_framework.pagination import PageNumberPagination

class CommentPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'size'
    page_query_param = 'page'  
    
    # sorting
    def paginate_queryset(self, queryset, request, view=None):
        if not queryset.ordered:
            queryset = queryset.order_by('created_at')
        return super().paginate_queryset(queryset, request, view=view)
    
    def get_paginated_response(self, data, url):

        response_data = {
                "type":"comments",
                "page": url,
                "id":f'{url}/comments',
                "page_number":self.page.number,
                "size": self.get_page_size(self.request),
                "count": len(data),
                "src": data
            }
        return Response(response_data, status=status.HTTP_200_OK)

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
def comment_list(request, AUTHOR_SERIAL=None, POST_SERIAL=None, POST_FQID=None):
    '''
    URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments
    eg. http://localhost:8000/api/authors/1/posts/1/comments
    eg. http://localhost:8000/api/authors/1/posts/1/comments?page=1&size=2
        GET [local, remote]: the comments on the post
    URL: ://service/api/posts/{POST_FQID}/comments
    eg. http://localhost:8000/api/posts/http://127.0.0.1:8000/api/authors/1/posts/1/comments
    eg. http://localhost:8000/api/posts/http://127.0.0.1:8000/api/authors/1/posts/1/comments?page=1&size=2
        GET [local, remote]: the comments on the post (that our server knows about)
    '''
    if AUTHOR_SERIAL is not None and POST_SERIAL is not None:
        author = get_object_or_404(Author, serial=AUTHOR_SERIAL)
        post = get_object_or_404(Post, serial=POST_SERIAL, author__serial=author.serial)
    elif POST_FQID is not None:
        post = get_object_or_404(Post, fqid=POST_FQID)
    else:
        return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
        
    url = post.fqid
    comments = Comment.objects.filter(post=post.id)
    
    paginator = CommentPagination()
    paged_comments = paginator.paginate_queryset(comments, request)
    serializer = CommentSerializer(paged_comments, many=True)
    return paginator.get_paginated_response(serializer.data, url)

@api_view(['GET'])    
def comment_detail_post(request,  AUTHOR_SERIAL=None, POST_SERIAL=None, REMOTE_COMMENT_FQID=None):
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/post/{POST_SERIAL}/comment/{REMOTE_COMMENT_FQID}
    eg. http://localhost:8000/api/authors/1/post/1/comment/http://127.0.0.1:8000/api/authors/2/commented/1
        GET [local, remote] get the comment}
    """
    
    if AUTHOR_SERIAL is not None and POST_SERIAL is not None and REMOTE_COMMENT_FQID is not None:
        author = get_object_or_404(Author, serial=AUTHOR_SERIAL)
        post = get_object_or_404(Post, serial=POST_SERIAL, author__serial=author.serial)
        comment = get_object_or_404(Comment, post__id=post.id, fqid=REMOTE_COMMENT_FQID)
    else:
        return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
    serializer = CommentSerializer(comment)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

# Commented API
@api_view(['GET', 'POST'])    
def author_comment_list(request, AUTHOR_SERIAL=None, AUTHOR_FQID=None):
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/commented
    eg. http://localhost:8000/api/authors/2/commented
    eg. http://localhost:8000/api/authors/2/commented?page=1&size=2
        GET [local, remote] get the list of comments author has made on:
            [local] any post
            [remote] public and unlisted posts
            paginated
        POST [local] if you post an object of "type":"comment", it will add your comment to the post whose ID is in the post field
            Then the node you posted it to is responsible for forwarding it to the correct inbox
    URL: ://service/api/authors/{AUTHOR_FQID}/commented
    eg. http://localhost:8000/api/authors/http://127.0.0.1:8000/api/authors/2/commented
    eg. http://localhost:8000/api/authors/http://127.0.0.1:8000/api/authors/2/commented?page=1&size=2
        GET [local] get the list of comments author has made on any post (that local node knows about)
    
    """
    if request.method == 'GET':
        if AUTHOR_SERIAL is not None:
            author = get_object_or_404(Author, serial=AUTHOR_SERIAL)  
        elif AUTHOR_FQID is not None:
            author = get_object_or_404(Author, fqid=AUTHOR_FQID)
            
        url = author.fqid
        comments = author.comments.all()
        
        paginator = CommentPagination()
        paged_comments = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(paged_comments, many=True)
        return paginator.get_paginated_response(serializer.data, url)

@api_view(['GET'])    
def comment_detail(request, AUTHOR_SERIAL=None, COMMENT_SERIAL=None, COMMENT_FQID=None):
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/commented/{COMMENT_SERIAL}
    eg. http://localhost:8000/api/authors/2/commented/1
        GET [local, remote] get this comment
    URL: ://service/api/commented/{COMMENT_FQID}
    eg. http://localhost:8000/api/commented/http://127.0.0.1:8000/api/authors/2/commented/1
        GET [local] get this comment
    """
    if AUTHOR_SERIAL is not None and COMMENT_SERIAL is not None: 
        author = get_object_or_404(Author, serial=AUTHOR_SERIAL)
        comment = get_object_or_404(Comment, serial=COMMENT_SERIAL, author=author.serial)
    elif COMMENT_FQID is not None:
        comment = get_object_or_404(Comment, fqid=COMMENT_FQID)
    else:
        return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CommentSerializer(comment)
    return Response(serializer.data, status=status.HTTP_200_OK)