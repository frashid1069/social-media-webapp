from rest_framework import serializers
from .models import Author


class AuthorSerializer(serializers.Serializer):
    id = serializers.AutoField()
    username = serializers.CharField()

    display_name = serializers.CharField()
    bio = serializers.TextField()
    github_url = serializers.URLField()
    profile_image = serializers.ImageField()

    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    
    
    def create(self, validated_data):
        author_instance = Author.objects.create(**validated_data) 
        return author_instance
        
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)