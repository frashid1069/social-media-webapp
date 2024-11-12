from rest_framework import serializers
from .models import Author, Post, Comment, Follow
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class SignUpSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(max_length=20, write_only=True)
    bio = serializers.CharField(allow_blank=True, allow_null=True, required=False, write_only=True)
    github_url = serializers.URLField(allow_blank=True, allow_null=True, required=False, write_only=True)
    class Meta:
        model = User
        fields = ['username', 'password', 'display_name', 'bio', 'github_url']
        
    def validate_username(self, value):
        """Ensure the username is unique in the User model."""
        if not value.strip():
            raise serializers.ValidationError("Username is required.")
        
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value
    
    def validate_password(self, value):
        """TODO: Ensure the password meets the requirements."""
        if not value.strip():
            raise serializers.ValidationError("Password is required.")
        return value
    
    def create(self, validated_data):
        """Create a user first, then create author, author object return as data."""
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(username=username, password=password)
        # User is inactive until approved by the admin
        user.is_active = False
        user.save()
        
        request = self.context.get('request')
        
        id = "http://test/api/authors" if not request else request.build_absolute_uri(f'/api/authors/{user.id}')
        host = "http://test/api/" if not request else request.build_absolute_uri("/api/")
        author = Author.objects.create(user=user, 
                                       username=username, 
                                       fqid=id,
                                       host=host,
                                       **validated_data)
        
        return author

        
# class LikeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Like
#         fields = "__all__"

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = "__all__"
        
