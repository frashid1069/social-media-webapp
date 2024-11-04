from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from . import models, serializers
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response


# Create your views here.
class AuthorView(ModelViewSet):
    queryset = models.Author.objects
    serializer_class = serializers.AuthorSerializer
    
    http_method_names = ['get', 'put']
    
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
        queryset = super().get_queryset() 
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            "type": "authors",
            "authors": serializer.data
        }
        return Response(response_data)
    
    @extend_schema(
        summary="Retrieve a single author",
        description="Fetch details of a specific author by ID.",
        responses={200: serializers.AuthorSerializer, 404: "Not Found"},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    
    
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
    