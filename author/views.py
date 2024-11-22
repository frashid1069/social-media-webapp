from rest_framework.viewsets import ModelViewSet
from author.serializers import Author, AuthorSerializer
from service.models import Node
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
import requests
from service.utils.jwt_auth import create_hearders
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view

class AuthorPagination(PageNumberPagination):
    page_size = 100  
    page_size_query_param = 'size'
    page_query_param = 'page'  
    
    def get_paginated_response(self, data):
        response_data = {
            "type": "authors",
            "authors": data
        }
        return Response(response_data, status=status.HTTP_200_OK)

class AuthorView(ModelViewSet):
    serializer_class = AuthorSerializer
    pagination_class = AuthorPagination
    http_method_names = ['get', 'put']
    # permission_classes = [AllowAny]
    
    def get_queryset(self, remote=False):
        if remote:
            queryset = Author.objects.filter(is_deleted=False, user__isnull=False)
        else:
            queryset = Author.objects.filter(is_deleted=False)
            
        return queryset.order_by('updated_at')
    
    @extend_schema(
        summary="Retrieve a list of authors",
        description="Fetches a list of all registered authors.",
        responses={200: AuthorSerializer(many=True)},
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
        # local request return local authors + other nodes' authors
        user = request.user
        if user.is_staff == False and user.is_active == True:
            
            allowed_nodes = Node.objects.filter(is_allowed=True)
            
            for node in allowed_nodes:
                headers = create_hearders(node)
                try:
                    response = requests.get(f"{node.url}authors/", headers=headers)
                    
                    if response.status_code == 200:
                        try:
                            authors = response.json().get("authors", [])
                            
                            for author in authors:
                                fqid = author.get("id")
                                if not fqid or Author.objects.filter(fqid=fqid).exists():
                                    continue
                                serializer = AuthorSerializer(data=author)

                                if serializer.is_valid():
                                    serializer.save()   
                                else:
                                    return Response({'errors': f"Author validation failed on host:{node.url}:{serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
                            
                        except ValidationError as e:
                            print(f"Validation Error: {e.detail}")
                            return Response({"error": e.detail},  status=status.HTTP_400_BAD_REQUEST)
                    else:
                        print(f"Failed to fetch authors from {node.url}: {response.status_code}")
                        Response(f"Failed to fetch authors from {node.url}: {response.status_code}", status=status.HTTP_400_BAD_REQUEST)
                        
                except requests.RequestException as e:
                    print(f"Error fetching authors from {node.url}: {e}")
                    
            queryset = self.get_queryset()      
            paged_queryset = self.paginate_queryset(queryset)
        
            if paged_queryset is not None:
                serializer = self.get_serializer(paged_queryset, many=True)
                return self.get_paginated_response(serializer.data)  
            
        # remote request return local authors only
        # filtering
        queryset = self.get_queryset(remote=True)
        paged_queryset = self.paginate_queryset(queryset)
        
        if paged_queryset is not None:
            serializer = self.get_serializer(paged_queryset, many=True)
            return self.get_paginated_response(serializer.data)
 
    @extend_schema(
        summary="Retrieve a single author",
        description="Fetch details of a specific author by ID.",
        responses={200: AuthorSerializer, 404: "Not Found"},
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
        serial = kwargs.get('AUTHOR_SERIAL')
        if serial:
            instance = get_object_or_404(Author, serial=serial, is_deleted=False, user__isnull=False)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        
        return super().retrieve(request, *args, **kwargs)
        
    @extend_schema(
        summary="Update an author",
        description="Update details of an existing author.",
        request= AuthorSerializer,
        responses={200: AuthorSerializer, 400: "Bad Request", 404: "Not Found"},
    )
    def update(self, request, *args, **kwargs):
        author = self.get_object()
        if author.user != request.user:
            raise PermissionDenied("You do not have permission to edit this profile.")
        return super().update(request, *args, **kwargs)
    
    
    
    
@api_view(['GET', 'PUT'])
def author_detail(request, AUTHOR_SERIAL=None, AUTHOR_FQID=None):
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/
    eg. http://localhost:8000/api/authors/1/
        GET [local, remote]: retrieve AUTHOR_SERIAL's profile
        PUT [local]: update AUTHOR_SERIAL's profile
    URL: ://service/api/authors/{AUTHOR_FQID}/
        GET [local]: retrieve AUTHOR_FQID's profile
    """
    
    
    if AUTHOR_SERIAL is not None:
        author = get_object_or_404(Author, serial=AUTHOR_SERIAL, is_deleted=False, user__isnull=False)
        serializer = AuthorSerializer(author)
        return Response(serializer.data)
    elif AUTHOR_FQID is not None:
        
        author_exists = Author.objects.filter(fqid=AUTHOR_FQID, is_deleted=False).exists()
        if author_exists:
            print(AUTHOR_FQID)
            author = get_object_or_404(Author, fqid=AUTHOR_FQID, is_deleted=False)
            serializer = AuthorSerializer(author)
        else:
            allowed_node_exists = Node.objects.filter(is_allowed=True, url__in=AUTHOR_FQID).exists()
            if allowed_node_exists:
                allowed_node = Node.objects.filter(is_allowed=True, url__in=AUTHOR_FQID)
                headers = create_hearders(allowed_node)
                
                try:
                    response = requests.get(AUTHOR_FQID, headers=headers)
                    
                    if response.status_code == 200:
                        try:
                            author = response.json()
                            if author.get("id"):
                                serializer = AuthorSerializer(data=author)
                                if serializer.is_valid():
                                    serializer.save()   
                                else:
                                    return Response({'errors': f"Author validation failed on host:{AUTHOR_FQID}:{serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
                            
                        except ValidationError as e:
                            print(f"Validation Error: {e.detail}")
                            return Response({"error": e.detail},  status=status.HTTP_400_BAD_REQUEST)
                    else:
                        print(f"Failed to fetch authors from {AUTHOR_FQID}: {response.status_code}")
                        return Response(f"Failed to fetch authors from {AUTHOR_FQID}: {response.status_code}", status=status.HTTP_400_BAD_REQUEST)
                        
                except requests.RequestException as e:
                    print(f"Error fetching authors from {AUTHOR_FQID}: {e}")
                    return Response(f"Error fetching authors from {AUTHOR_FQID}: {e}")
            else:
                print(f"Node object not found for {AUTHOR_FQID}")
                return Response(f"Node object not found for {AUTHOR_FQID}", status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.data)
            
                