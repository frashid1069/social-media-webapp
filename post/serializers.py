from rest_framework import serializers
from author.serializers import AuthorSerializer 
from .models import Post, Repost
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
        
    def create(self, validated_data):
        post = Post.objects.create(**validated_data)
        
        if post.content_type == 'image/jpeg' and post.content:
            request = self.context.get('request')
            author_serial = post.author.id
            if request:
                # Generate the url based on author ID and post ID
                image_url = request.build_absolute_uri(f'/api/post/image/?author_id={author_serial}&post_id={post.id}')
                post.image_url = image_url
                post.save()  

        return post

class RepostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repost
        fields = "__all__"
        
   
