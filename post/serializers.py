from rest_framework import serializers
from .models import Post, Repost

class PostSerializer(serializers.ModelSerializer):
    can_share = serializers.SerializerMethodField()

    class Meta:
        model = Post
<<<<<<< HEAD
        fields = "__all__"
        

class RepostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repost
        fields = "__all__"
        
   
=======
        fields = ["id", "author", "title", "content", "content_type", "image_content", "created_at", "updated_at", "visibility", "is_deleted", "can_share"]

    def get_can_share(self, obj):
        # Only public posts are shareable
        return obj.visibility == 'public'
>>>>>>> 67114780eddd9c10fb5f664410c78dbcc5ac05c4
