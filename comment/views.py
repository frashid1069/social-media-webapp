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
from service.utils.push import push
from rest_framework.exceptions import ValidationError

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
@api_view(['GET'])    
def comment_list(request, AUTHOR_SERIAL=None, POST_SERIAL=None, POST_FQID=None):
    """
    Retrieves comments on a specific post, either locally or remotely.

    URL Patterns:
    1. ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments
       Example: 
       - http://localhost:8000/api/authors/1/posts/1/comments
       - http://localhost:8000/api/authors/1/posts/1/comments?page=1&size=2
       - GET [local, remote]: Retrieves comments for the post identified by `AUTHOR_SERIAL` and `POST_SERIAL`.

    2. ://service/api/posts/{POST_FQID}/comments
       Example:
       - http://localhost:8000/api/posts/http://127.0.0.1:8000/api/authors/1/posts/1/comments
       - http://localhost:8000/api/posts/http://127.0.0.1:8000/api/authors/1/posts/1/comments?page=1&size=2
       - GET [local, remote]: Retrieves comments for the post identified by `POST_FQID`.

    Parameters:
    - AUTHOR_SERIAL: (Optional) Numeric identifier for the author.
    - POST_SERIAL: (Optional) Numeric identifier for the post.
    - POST_FQID: (Optional) Fully qualified identifier (FQID) for the post.

    Returns:
    - Paginated list of comments (HTTP 200) with serialized data if successful.
    - HTTP 404 if the post or comments are not found.
    """
    if AUTHOR_SERIAL is not None and POST_SERIAL is not None:
        author = get_object_or_404(Author, serial=AUTHOR_SERIAL, is_deleted=False)
        post = get_object_or_404(Post, serial=POST_SERIAL, author__serial=author.serial, is_deleted=False)
    elif POST_FQID is not None:
        post = get_object_or_404(Post, fqid=POST_FQID, is_deleted=False)
    else:
        return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
        
    url = post.fqid
    comments = Comment.objects.filter(post=post.fqid)
    
    paginator = CommentPagination()
    paged_comments = paginator.paginate_queryset(comments, request)
    serializer = CommentSerializer(paged_comments, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data, url)

@api_view(['GET'])    
def comment_detail_post(request,  AUTHOR_SERIAL=None, POST_SERIAL=None, REMOTE_COMMENT_FQID=None):
    """
    Retrieves a specific comment on a post, either locally or remotely.

    URL Pattern:
    - ://service/api/authors/{AUTHOR_SERIAL}/post/{POST_SERIAL}/comment/{REMOTE_COMMENT_FQID}
      Example:
      - http://localhost:8000/api/authors/1/post/1/comment/http://127.0.0.1:8000/api/authors/2/commented/1
      - GET [local, remote]: Retrieves the comment specified by `REMOTE_COMMENT_FQID` for the post 
        identified by `AUTHOR_SERIAL` and `POST_SERIAL`.

    Parameters:
    - AUTHOR_SERIAL: Numeric identifier for the author.
    - POST_SERIAL: Numeric identifier for the post.
    - REMOTE_COMMENT_FQID: Fully qualified identifier (FQID) for the comment.

    Returns:
    - HTTP 200 with serialized comment data if successful.
    - HTTP 404 if the author, post, or comment is not found.
    - HTTP 400 if the request is invalid.
    """
    
    if AUTHOR_SERIAL is not None and POST_SERIAL is not None and REMOTE_COMMENT_FQID is not None:
        author = get_object_or_404(Author, serial=AUTHOR_SERIAL, is_deleted=False)
        post = get_object_or_404(Post, serial=POST_SERIAL, author__serial=author.serial, is_deleted=False)
        comment = get_object_or_404(Comment, post=post.fqid, fqid=REMOTE_COMMENT_FQID)
    else:
        return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
    serializer = CommentSerializer(comment, context={'request': request})
    
    return Response(serializer.data, status=status.HTTP_200_OK)

# Commented API
@api_view(['GET', 'POST'])    
def author_comment_list(request, AUTHOR_SERIAL=None, AUTHOR_FQID=None):
    """
    Handles retrieval and creation of comments made by an author.

    URL Patterns:
    1. ://service/api/authors/{AUTHOR_SERIAL}/commented
       Example:
       - http://localhost:8000/api/authors/2/commented
       - http://localhost:8000/api/authors/2/commented?page=1&size=2
       - GET [local, remote]: Retrieves a paginated list of comments made by the author.
         - Local: Includes comments made on any post.
         - Remote: Includes comments on public and unlisted posts.
       - POST [local]: Creates a new comment for the specified post.

    2. ://service/api/authors/{AUTHOR_FQID}/commented
       Example:
       - http://localhost:8000/api/authors/http://127.0.0.1:8000/api/authors/2/commented
       - http://localhost:8000/api/authors/http://127.0.0.1:8000/api/authors/2/commented?page=1&size=2
       - GET [local]: Retrieves a paginated list of comments made by the author known to the local node.

    Parameters:
    - AUTHOR_SERIAL: Numeric identifier for the author (local).
    - AUTHOR_FQID: Fully qualified identifier (FQID) for the author (remote).

    Returns:
    - GET:
      - HTTP 200: Paginated list of serialized comments.
    - POST:
      - HTTP 201: Serialized comment data if successful.
      - HTTP 403: If the user is unauthorized to post on behalf of the author.
      - HTTP 400: If the request data is invalid.
    """
    if request.method == 'GET':
        if AUTHOR_SERIAL is not None:
            author = get_object_or_404(Author, serial=AUTHOR_SERIAL, is_deleted=False)  
        elif AUTHOR_FQID is not None:
            author = get_object_or_404(Author, fqid=AUTHOR_FQID, is_deleted=False)
            
        url = author.fqid
        comments = author.comments.all()

        paginator = CommentPagination()
        paged_comments = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(paged_comments, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data, url)

    elif request.method == 'POST':
        if AUTHOR_SERIAL is not None:
            author = get_object_or_404(Author, serial=AUTHOR_SERIAL, is_deleted=False)
        else:
            return Response({"error": "AUTHOR_SERIAL is not provided"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        if not request.user.is_authenticated or request.user.author.serial != AUTHOR_SERIAL:
            return Response({"detail": "You are not authorized to create a post for this author."}, status=status.HTTP_403_FORBIDDEN)

        # try:
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=author)
            # push to inbox
            push(author, request, serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        #    # error handling
        #     else:
        #         print(f"Post validation failed {serializer.errors}")
        #         return Response({'errors': f"Post validation failed {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        # except ValidationError as e:
        #     print(f"Validation Error: {e.detail}")
        #     return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     print(f"Unexpected Error: {e}")
        #     return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


@api_view(['GET'])    
def comment_detail(request, AUTHOR_SERIAL=None, COMMENT_SERIAL=None, COMMENT_FQID=None):
    """
    Retrieves a specific comment either by its serial or FQID.

    URL Patterns:
    1. ://service/api/authors/{AUTHOR_SERIAL}/commented/{COMMENT_SERIAL}
       Example:
       - http://localhost:8000/api/authors/2/commented/1
       - GET [local, remote]: Retrieves the comment identified by `COMMENT_SERIAL` 
         associated with the author identified by `AUTHOR_SERIAL`.

    2. ://service/api/commented/{COMMENT_FQID}
       Example:
       - http://localhost:8000/api/commented/http://127.0.0.1:8000/api/authors/2/commented/1
       - GET [local]: Retrieves the comment identified by its fully qualified identifier (FQID).

    Parameters:
    - AUTHOR_SERIAL: Numeric identifier for the author.
    - COMMENT_SERIAL: Numeric identifier for the comment (local).
    - COMMENT_FQID: Fully qualified identifier (FQID) for the comment.

    Returns:
    - HTTP 200 with serialized comment data if successful.
    - HTTP 404 if the comment or author is not found.
    - HTTP 400 if the request is invalid.
    """
    if AUTHOR_SERIAL is not None and COMMENT_SERIAL is not None: 
        author = get_object_or_404(Author, serial=AUTHOR_SERIAL, is_deleted=False)
        comment = get_object_or_404(Comment, serial=COMMENT_SERIAL, author=author.serial)
    elif COMMENT_FQID is not None:
        comment = get_object_or_404(Comment, fqid=COMMENT_FQID)
    else:
        return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CommentSerializer(comment, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)