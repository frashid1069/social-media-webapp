from rest_framework import serializers
from .models import Author, Post, Comment, Like, Follow, Inbox
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# class AuthorSerializer(serializers.Serializer):
#     id = serializers.AutoField()
#     username = serializers.CharField()

#     display_name = serializers.CharField()
#     bio = serializers.TextField()
#     github_url = serializers.URLField()
#     profile_image = serializers.ImageField()

#     created_at = serializers.DateTimeField()
#     updated_at = serializers.DateTimeField()
    
    
#     def create(self, validated_data):
#         author_instance = Author.objects.create(**validated_data) 
#         return author_instance
        
#     def update(self, instance, validated_data):
#         return super().update(instance, validated_data)

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['username', 'password', 'display_name', 'bio', 'github_url', 'profile_image']
        
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

        author = Author.objects.create(user=user, username=username, password=password, **validated_data)
        
        return author

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"
        
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
        
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = "__all__"
        
class InboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inbox
        fields = "__all__"