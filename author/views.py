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
    
    def list(self, request, *args, **kwargs):
        """
        Handles the retrieval of author profiles (local and remote) in a paginated format.

        URL:
        - ://service/api/authors/
        Example: http://localhost:8000/api/authors?page=3&size=1

        Behavior:
        - GET [local, remote]: Retrieves all profiles on the node (paginated).
        - Local request:
            - Returns local authors combined with authors from other allowed nodes.
        - Remote request:
            - Returns local authors only.

        Query Parameters:
        - page: The current page number (optional).
        - size: The number of items per page (optional).

        User Conditions:
        - If the user is active and not a staff member:
        - Fetches and integrates authors from allowed nodes into the local database.
        - Ensures no duplicate authors are saved.

        Returns:
        - HTTP 200 with paginated serialized author data if successful.
        - HTTP 400/500 for errors encountered during remote author validation or processing.

        """
            # local request return local authors + other nodes' authors
        user = request.user
        if user.is_staff == False and user.is_active == True:
            
            allowed_nodes = Node.objects.filter(is_allowed=True)
            
            for node in allowed_nodes:
                headers = create_hearders(node)
                try:
                    response = requests.get(f"{node.url}authors/", headers=headers, timeout=10)
                    response.raise_for_status()
                    if response.status_code == 200:
                        authors = response.json().get("authors", [])
                        for author in authors:
                            fqid = author.get("id")
                            author_exists = Author.objects.filter(fqid=fqid).exists()
                            if author_exists:
                                continue
                            try:
                                serializer = AuthorSerializer(data=author)

                                if serializer.is_valid():
                                    serializer.save()   
                                else:
                                    print(f"Author validation failed {serializer.errors}")
                                    return Response({'errors': f"Author validation failed{node.url}: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
                        
                            except ValidationError as e:
                                print(f"Validation Error: {e.detail}")
                                return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
                            except Exception as e:
                                print(f"Unexpected Error: {e}")
                                print(f"Problematic Data: {author}")
                                return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:
                        print(f"Failed to fetch authors from {node.url}: {response.status_code}")
                        
                except requests.RequestException as e:
                    print(f"Error fetching authors from {node.url}: {e}")
                    continue
                    
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
    Handles retrieval and update of author profiles.

    URL Patterns:
    1. ://service/api/authors/{AUTHOR_SERIAL}/
       Example: http://localhost:8000/api/authors/1/
       - GET [local, remote]: Retrieves the profile of the author identified by `AUTHOR_SERIAL`.
         - Conditions:
           - The author must exist.
           - `is_deleted` must be False.
           - The associated user must not be null.
       - PUT [local]: Updates the profile of the author identified by `AUTHOR_SERIAL`.

    2. ://service/api/authors/{AUTHOR_FQID}/
       Example: http://remote-service/api/authors/abc123/
       - GET [local]: Retrieves the profile of the author identified by `AUTHOR_FQID`.
       - GET [remote]: If the author does not exist locally, attempts to fetch it from a remote service.

    Parameters:
    - AUTHOR_SERIAL: (Optional) Numeric identifier for a local author.
    - AUTHOR_FQID: (Optional) Fully qualified identifier (URL) for an author.

    Returns:
    - HTTP 200 with serialized author data if successful.
    - HTTP 400/404 if an error occurs.
    """
    
    
    if AUTHOR_SERIAL is not None:
        if request.method == "GET":
            author = get_object_or_404(Author, serial=AUTHOR_SERIAL, is_deleted=False, user__isnull=False)
            serializer = AuthorSerializer(author)
            return Response(serializer.data)
        if request.method == "PUT":
            author = get_object_or_404(Author, serial=AUTHOR_SERIAL, is_deleted=False, user__isnull=False)
            serializer = AuthorSerializer(author,data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
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
            
                
