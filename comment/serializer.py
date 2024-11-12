from rest_framework import serializers
from comment.models import Comment
from author.serializers import AuthorSerializer 



class CommentSerializer(serializers.ModelSerializer):
    
    id = serializers.URLField(source='fqid', read_only=True)
    contentType = serializers.CharField(source='content_type')
    comment = serializers.CharField(source='content', required=True)
    author = AuthorSerializer(read_only=True)
    likes = serializers.SerializerMethodField(read_only=True)
    published = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            "type",
            "author",
            "comment",
            "contentType",
            "published",
            "id",
            "post",
            "likes",        
        ]
        
    def get_likes(self, obj):
    # likes = Like.objects.filter(post=obj)
    # return LikeSerializer(likes, many=True).data
        return "likes"