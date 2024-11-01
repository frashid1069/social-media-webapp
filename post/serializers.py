from rest_framework import serializers
from author.serializers import AuthorSerializer 
from .models import Post, Repost

class PostSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Post
        fields = "__all__"

        #exclude = ['created_at', 'updated_at', 'is_deleted']

    def get_can_share(self, obj):
        # Only public posts are shareable
        return obj.visibility == 'public'
        fields = "__all__"
        

class RepostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repost
        fields = "__all__"
        
   
