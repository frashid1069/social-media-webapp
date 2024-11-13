from rest_framework import serializers
from .models import Like
from author.serializers import AuthorSerializer
from comment.models import Comment


class LikeSerializer(serializers.ModelSerializer):
    id = serializers.URLField(source='fqid', read_only=True)
    author = AuthorSerializer(read_only=True)
    published = serializers.DateTimeField(source='created_at', read_only=True)
    object = serializers.URLField(required=True)
        
    class Meta:
        model = Like
        fields = [
            "type",
            "author",
            "published",
            "id",
            "object",       
        ]