from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    can_share = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "author", "title", "content", "content_type", "image_content", "created_at", "updated_at", "visibility", "is_deleted", "can_share"]

    def get_can_share(self, obj):
        # Only public posts are shareable
        return obj.visibility == 'public'
