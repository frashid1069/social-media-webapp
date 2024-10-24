from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.viewsets import ModelViewSet
from comment.models import Comment
from comment.serializer import CommentSerializer

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
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a comment",
        description="Delete a comment by its ID.",
        responses={204: None, 404: "Not Found"},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
