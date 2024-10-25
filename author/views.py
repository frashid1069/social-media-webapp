from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from . import models, serializers
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.exceptions import PermissionDenied


# Create your views here.
class AuthorView(ModelViewSet):
    # authentication_classes = []
    # permission_classes = []
    queryset = models.Author.objects
    serializer_class = serializers.AuthorSerializer
    
    @extend_schema(
        summary="Retrieve a list of authors",
        description="Fetches a list of all registered authors.",
        responses={200: serializers.AuthorSerializer(many=True)},
        parameters=[
            OpenApiParameter(name="limit", description="Limit the number of authors", type=int, required=False),
            OpenApiParameter(name="offset", description="Offset for pagination", type=int, required=False),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Retrieve a single author",
        description="Fetch details of a specific author by ID.",
        responses={200: serializers.AuthorSerializer, 404: "Not Found"},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create a new author",
        description="Register a new author with the required details.",
        request=serializers.AuthorSerializer,
        responses={201: serializers.AuthorSerializer, 400: "Bad Request"},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update an author",
        description="Update details of an existing author.",
        request=serializers.AuthorSerializer,
        responses={200: serializers.AuthorSerializer, 400: "Bad Request", 404: "Not Found"},
    )
    def update(self, request, *args, **kwargs):
        author = self.get_object()
        if author.user != request.user:
            raise PermissionDenied("You do not have permission to edit this profile.")
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete an author",
        description="Soft-delete or permanently delete an author by ID.",
        responses={204: None, 404: "Not Found"},
    )
    def destroy(self, request, *args, **kwargs):
        author = self.get_object()
        if author.user != request.user:
            print(author.user, request.user)
            raise PermissionDenied("You do not have permission to delete this profile.")
        return super().destroy(request, *args, **kwargs)