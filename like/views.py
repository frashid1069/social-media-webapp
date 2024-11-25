from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.viewsets import ModelViewSet
from . import models, serializers
from .serializers import Like, LikeSerializer, Comment
from .models import Post, Author
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from service.utils.push import push
from rest_framework.exceptions import ValidationError

class LikePagination(PageNumberPagination):
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
        "type":"likes",
        "page": url,
        "id": f'{url}/likes',
        "page_number":self.page.number,
        "size": self.get_page_size(self.request),
        "count": len(data),
        "src": data
    }
        return Response(response_data, status=status.HTTP_200_OK)


class LikeView(ModelViewSet):
    queryset = models.Like.objects
    serializer_class = serializers.LikeSerializer

    @extend_schema(
        summary="Retrieve a list of likes",
        description="""
        Retrieve a list of likes, with optional filtering.
        - If `author_id` and `post_id` are provided, returns likes for a particular post made by the specified author.
        - If `author_id` is provided, returns all likes made by that author.
        - If `post_id` is provided, returns all likes for the specified post.
        """,
        parameters=[
            OpenApiParameter(name="author_id", description="Filter likes by the author's ID", required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name="post_id", description="Filter likes by the post's ID", required=False, type=OpenApiTypes.INT),
        ],
        responses={200: serializers.LikeSerializer(many=True), 400: "Bad Request"},
    )
    def get_queryset(self):
        # Get the base queryset from the parent class
        queryset = super().get_queryset()
        # Extract query parameters from the request
        post_id = self.request.query_params.get('post_id')
        author_id = self.request.query_params.get('author_id')

        # If both 'author_id' and 'post_id' are provided in the request query parameters:
        # Filter the queryset to return likes where both the author ID and post ID match
        # i.e., likes made by a specific author on a specific post.
        # ~post/?author_id=<pk>&post_id=<pk> (likes for a particular post made by a particular author)
        if author_id and post_id:
            queryset = queryset.filter(author__id=author_id, post__id=post_id)

        # If only 'author_id' is provided in the query parameters:
        # Filter the queryset to return all likes made by that specific author.
        # ~post/?author_id=<pk> (all likes made by a particular author)
        elif author_id:
            queryset = queryset.filter(author__id=author_id)
        
        # If only 'post_id' is provided in the query parameters:
        # Filter the queryset to return all likes for the specified post.
        # ~post/?post_id=<pk> (all likes for a particular post)
        elif post_id:
            queryset = queryset.filter(post__id=post_id)

        return queryset.order_by("created_at") # return the filtered queryset
    
    @extend_schema(
        summary="Create a new like",
        description="Create a new like for a post by an author.",
        request=serializers.LikeSerializer,
        responses={201: serializers.LikeSerializer, 400: "Bad Request"},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="Retrieve a single like",
        description="Fetch the details of a like by its ID.",
        responses={200: serializers.LikeSerializer, 404: "Not Found"},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete a like",
        description="Delete a like by its ID.",
        responses={204: None, 404: "Not Found"},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

'''
Likes API
'''
@api_view(['GET'])
def who_liked_this_post(request, AUTHOR_SERIAL=None, POST_SERIAL=None, POST_FQID=None):
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/likes
    eg. http://localhost:8000/api/authors/1/posts/1/likes
    eg. http://localhost:8000/api/authors/1/posts/1/likes?page=2&size=1
        GET [local, remote] a list of likes from other authors on author_id's post post_id
    URL: ://service/api/posts/{POST_FQID}/likes
    eg. http://localhost:8000/api/posts/http://127.0.0.1:8000/api/authors/1/posts/1/likes
    eg. http://localhost:8000/api/posts/http://127.0.0.1:8000/api/authors/1/posts/1/likes?page=2&size=1
        GET [local] a list of likes from other authors on AUTHOR_SERIAL's post POST_SERIAL
    """
    
    if AUTHOR_SERIAL is not None and POST_SERIAL is not None:
        try:
            post = Post.objects.get(serial=POST_SERIAL, author__serial=AUTHOR_SERIAL)
            url = post.fqid
            likes_of_object = Like.objects.filter(object=url)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found with AUTHOR_SERIAL/POST_SERIAL."}, status=status.HTTP_404_NOT_FOUND)
    elif POST_FQID is not None:
        try:
            likes_of_object = Like.objects.filter(object=POST_FQID)
            url = POST_FQID
        except:
            return Response({"detail": "Post not found with POST_FQID."}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
    
    paginator = LikePagination()
    paged_likes = paginator.paginate_queryset(likes_of_object, request)
    serializer = LikeSerializer(paged_likes, many=True)
    return paginator.get_paginated_response(serializer.data, url)
    

@api_view(['GET'])
def who_liked_this_comment(request, AUTHOR_SERIAL, POST_SERIAL, COMMENT_FQID):
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments/{COMMENT_FQID}/likes
    eg. http://localhost:8000/api/authors/1/posts/1/comments/http://127.0.0.1:8000/api/authors/3/commented/1/likes
    eg. http://localhost:8000/api/authors/1/posts/1/comments/http://127.0.0.1:8000/api/authors/3/commented/1/likes?page=1&size=1
        GET [local, remote] a list of likes from other authors on AUTHOR_SERIAL's post POST_SERIAL comment COMMENT_SERIAL
    """
    post = get_object_or_404(Post, serial=POST_SERIAL, author__serial=AUTHOR_SERIAL)
    comment = get_object_or_404(Comment, fqid=COMMENT_FQID, post__id=post.id)
    url = comment.fqid
    
    likes_of_object = Like.objects.filter(object=url)

    paginator = LikePagination()
    paged_likes = paginator.paginate_queryset(likes_of_object, request)
    serializer = LikeSerializer(paged_likes, many=True)
    return paginator.get_paginated_response(serializer.data, url)

'''
Liked API
'''
@api_view(['GET', 'POST'])
def things_liked_by_author(request, AUTHOR_SERIAL=None, AUTHOR_FQID=None):
    """
    "Things Liked By Author"
    URL: ://service/api/authors/{AUTHOR_SERIAL}/liked
    eg. http://localhost:8000/api/authors/1/liked
    eg. http://localhost:8000/api/authors/1/liked?page=1&size=1
        GET [local, remote] a list of likes by AUTHOR_SERIAL
    URL: ://service/api/authors/{AUTHOR_FQID}/liked
    eg. http://localhost:8000/api/authors/http://127.0.0.1:8000/api/authors/1/liked
    eg. http://localhost:8000/api/authors/http://127.0.0.1:8000/api/authors/1/liked?page=1&size=1
        GET [local] a list of likes by AUTHOR_FQID
    """
    if AUTHOR_SERIAL is not None:
        if request.method == 'GET':
            try:
                author = Author.objects.get(serial=AUTHOR_SERIAL)
            except Author.DoesNotExist:
                return Response({"detail": "Author not found with AUTHOR_SERIAL."}, status=status.HTTP_404_NOT_FOUND)
            
        elif request.method == 'POST':
            # authentication
            current_author = getattr(request.user, 'author', None)
            author = get_object_or_404(Author, serial=AUTHOR_SERIAL, is_deleted=False)
            if current_author == author:
                try:
                    serializer = LikeSerializer(data=request.data)
                    if serializer.is_valid():
                        serializer.save(author=author)
                        # push to inbox
                        push(author, request, serializer.data)
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
            else:
                return Response({"detail": f"You are not authorized to create a like for this author {author}."}, status=status.HTTP_403_FORBIDDEN)
                
            

                

            
            
    elif AUTHOR_FQID is not None:
        try:
            author = Author.objects.get(fqid=AUTHOR_FQID)
        except Author.DoesNotExist:
            return Response({"detail": "Author not found with AUTHOR_FQID."}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"error": "AUTHOR_SERIAL/AUTHOR_FQID is not provided"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    likes_of_object = author.likes.all()
    url = author.fqid
        
    paginator = LikePagination()
    paged_likes = paginator.paginate_queryset(likes_of_object, request)
    serializer = LikeSerializer(paged_likes, many=True)
    return paginator.get_paginated_response(serializer.data, url)

@api_view(['GET'])
def like_detail(request, AUTHOR_SERIAL=None, LIKE_SERIAL=None, LIKE_FQID=None):
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/liked/{LIKE_SERIAL}
    eg. http://localhost:8000/api/authors/3/liked/1
        GET [local, remote] a single like
    URL: ://service/api/liked/{LIKE_FQID}
    eg. http://localhost:8000/api/liked/http://127.0.0.1:8000/api/authors/3/liked/1
        GET [local] a single like
    """
    if LIKE_FQID is not None:
        try:
            like = Like.objects.get(fqid=LIKE_FQID)
        except Like.DoesNotExist:
            return Response({"detail": "Like not found with LIKE_FQID."}, status=status.HTTP_404_NOT_FOUND)
    elif AUTHOR_SERIAL is not None and LIKE_SERIAL is not None:
        try:
            author = Author.objects.get(serial=AUTHOR_SERIAL)
            like = Like.objects.get(serial=LIKE_SERIAL, author__serial=author.serial)
        except Like.DoesNotExist:
            return Response({"detail": "Like not found with AUTHOR_SERIAL/LIKE_SERIAL."}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"detail": "Like not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = LikeSerializer(like)
    return Response(serializer.data, status=status.HTTP_200_OK)