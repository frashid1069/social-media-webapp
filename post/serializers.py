from rest_framework import serializers
from author.serializers import AuthorSerializer 
from .models import Post
from like.serializers import Like, LikeSerializer
from comment.serializer import Comment, CommentSerializer

class PostSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    id = serializers.URLField(source='fqid', read_only=True)
    page = serializers.SerializerMethodField(read_only=True)
    description = serializers.CharField(required=True)
    contentType = serializers.CharField(source='content_type')
    content = serializers.CharField(required=True)
    author = AuthorSerializer(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)
    likes = serializers.SerializerMethodField(read_only=True)
    published = serializers.DateTimeField(source='created_at', read_only=True)
    visibility = serializers.CharField(required=True)
    
    class Meta:
        
        model = Post
        fields = [
            "type",
            "title",
            "id",
            "page",
            "description",
            "contentType",
            "content",
            "author",
            "comments",
            "likes",
            "published",
            "visibility",
        ]
        
    def get_page(self, obj):
        return "http://nodebbbb/authors/222/posts/293"
    
    def get_likes(self, obj):
        likes = Like.objects.filter(object=obj.fqid)
        return LikeSerializer(likes, many=True).data
    
    def get_comments(self, obj):
        comments = Comment.objects.filter(post=obj.id)
        return CommentSerializer(comments, many=True).data

        
    

    def get_can_share(self, obj):
        # Only public posts are shareable
        return obj.visibility == 'public'
        fields = "__all__"