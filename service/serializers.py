from rest_framework import serializers
from .models import Author, Post, Comment, Like, Follow, Inbox


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