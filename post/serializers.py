from rest_framework import serializers
from .models import Post, Repost

class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = "__all__"
        

class RepostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repost
        fields = "__all__"
        
   
