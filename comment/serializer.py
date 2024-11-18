from rest_framework import serializers
from comment.models import Comment
from author.serializers import AuthorSerializer 
from like.serializers import Like, LikeSerializer



class CommentSerializer(serializers.ModelSerializer):
    
    id = serializers.URLField(source='fqid', read_only=True)
    contentType = serializers.CharField(source='content_type', required=True)
    comment = serializers.CharField(source='content', required=True)
    author = AuthorSerializer(read_only=True)
    published = serializers.DateTimeField(source='created_at', read_only=True)
    post = serializers.URLField(source="post.fqid", read_only=True)
    likes = serializers.SerializerMethodField(read_only=True)
    
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
        likes = Like.objects.filter(object=obj.fqid)
        return LikeSerializer(likes, many=True).data
    
    # def create(self, validated_data):
    #     comment = Comment.objects.create(validated_data)
        
        
    #     return comment