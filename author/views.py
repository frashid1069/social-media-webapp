from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from . import models, serializers
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

class AuthorPagination(PageNumberPagination):
    page_size = 5  
    page_size_query_param = 'size'
    page_query_param = 'page'  
    
    def get_paginated_response(self, data):
        response_data = {
            "type": "authors",
            "authors": data
        }
        return Response(response_data, status=status.HTTP_200_OK)

class AuthorView(ModelViewSet):
    queryset = models.Author.objects
    serializer_class = serializers.AuthorSerializer
    pagination_class = AuthorPagination
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
        """
        URL: ://service/api/authors/
        eg. http://localhost:8000/api/authors?page=3&size=1
            GET [local, remote]: retrieve all profiles on the node (paginated)
                page: how many pages
                size: how big is a page
        """
        queryset = super().get_queryset().filter(is_deleted=False)
        paged_queryset = self.paginate_queryset(queryset)
        if paged_queryset is not None:
            serializer = self.get_serializer(paged_queryset, many=True)
            return self.get_paginated_response(serializer.data)
        

    
    @extend_schema(
        summary="Retrieve a single author",
        description="Fetch details of a specific author by ID.",
        responses={200: serializers.AuthorSerializer, 404: "Not Found"},
    )
    def retrieve(self, request, *args, **kwargs):
        """
        URL: ://service/api/authors/{AUTHOR_SERIAL}/
        eg. http://localhost:8000/api/authors/1/
            GET [local, remote]: retrieve AUTHOR_SERIAL's profile
            PUT [local]: update AUTHOR_SERIAL's profile
        URL: ://service/api/authors/{AUTHOR_FQID}/
            GET [local]: retrieve AUTHOR_FQID's profile
        """
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
    