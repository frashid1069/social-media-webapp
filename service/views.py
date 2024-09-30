from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Author
from .serializers import AuthorSerializer

# Later on, the index function will be used to handle incoming requests to polls/ and it will return the hello world string shown below.
def index(request):
    return HttpResponse("Hello, world. You're at the service index.")

class AuthorsView(APIView):
    def get(self, request):
        author_list = Author.objects.all()
        
        serializer = AuthorSerializer(instance=author_list, many=True)
        return Response(serializer.data)