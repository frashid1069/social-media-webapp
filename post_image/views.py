from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, action
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, status
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from .serializers import ImagePost, ImagePostSerializer
import base64


class ImagePostView(ModelViewSet):
    queryset = ImagePost.objects
    serializer_class = ImagePostSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]  # Allows public access for reading
    
    def create(self, request, *args, **kwargs):
        image_file = request.FILES.get('image_content')
        if not image_file:
            return Response({"error": "An image file is required."},
                            status=status.HTTP_400_BAD_REQUEST)
            
        # base64 encode
        image_data = image_file.read()
        base64_data = f"data:{image_file.content_type};base64," + base64.b64encode(image_data).decode('utf-8')
        
        # request.data is immutable
        modified_data = request.data.copy()  
        modified_data['image_content'] = base64_data 
        serializer = self.get_serializer(data=modified_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], url_path='image', url_name='get_image')
    def get_image(self, request):
        author_id = request.query_params.get('author_id')
        image_id = request.query_params.get('image_id')
        
        # Retrieve the image post based on author_id and image_id
        image_post = get_object_or_404(ImagePost, author=author_id, id=image_id)
        
        base64_data = image_post.image_content.split(",")[1]  # Get the data part
        image_binary = base64.b64decode(base64_data)  # Decode base64 to binary
        content_type = image_post.image_content.split(";")[0][5:]  # Extract MIME type (e.g., "image/jpeg")

        # Return the binary data with the appropriate content type
        return HttpResponse(image_binary, content_type=content_type)

@api_view(['GET'])
def get_image(request):
    author_id = request.GET.get('author_id')
    image_id = request.GET.get('image_id')
    print(author_id, image_id)
    image_post = get_object_or_404(ImagePost, author=author_id, id=image_id)
    print(image_post)
    return HttpResponse(image_post.image_content)