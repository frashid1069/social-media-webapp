from rest_framework import serializers
from author.serializers import AuthorSerializer, Author
from .models import Post
from like.serializers import Like, LikeSerializer
from comment.serializer import Comment, CommentSerializer
from like.views import LikePagination
from comment.views import CommentPagination

class PostSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    id = serializers.URLField(source='fqid', read_only=True)
    page = serializers.URLField(source='fqid',read_only=True)
    description = serializers.CharField(required=False)
    contentType = serializers.CharField(required=True, source='content_type')
    content = serializers.CharField(required=True)
    author = AuthorSerializer(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)

    # comments = serializers.ListSerializer(
    #     child=CommentSerializer(), required=False, allow_null=True
    # )
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
        
        
    def get_likes(self, obj):
        likes_queryset = Like.objects.filter(object=obj.fqid)
        paginator = LikePagination()
        request = self.context.get('request', None)
        page = paginator.paginate_queryset(likes_queryset, request, view=None)

        url = self.context['request'].build_absolute_uri().strip('/')
        paginated_response = paginator.get_paginated_response(
            LikeSerializer(page, many=True).data,
            url=url
        )
        return paginated_response.data
    
    def get_comments(self, obj):
        comments_queryset = Comment.objects.filter(post=obj.fqid)
        paginator = CommentPagination()
        request = self.context.get('request', None)
        page = paginator.paginate_queryset(comments_queryset, request, view=None)

        url = self.context['request'].build_absolute_uri().strip('/')
        paginated_response = paginator.get_paginated_response(
            CommentSerializer(page, many=True, context={'request': request}).data,
            url=url
        )
        return paginated_response.data
    
    def validate_visibility(self, value):
        # Normalize value to lowercase and ensure it matches a valid choice
        normalized_value = value.lower()
        print(normalized_value)
        valid_choices = [choice[0] for choice in Post.VISIBILITY_CHOICES]
        if normalized_value not in valid_choices:
            raise serializers.ValidationError(f"Invalid visibility value: {value}")
        return normalized_value
    
    def validate_contentType(self, value):
        """
        Custom validator for contentType.
        If the contentType is 'image/jpeg', convert it to 'image/png;base64'.
        """
        if value == 'image/jpeg':
            return 'image/jpeg;base64'
        elif value == 'image/png':
            return 'image/png;base64'
        return value
    
    def to_representation(self, instance):
        """
        Override representation to return visibility in uppercase.
        """
        representation = super().to_representation(instance)
        representation['visibility'] = instance.visibility_display
        return representation
    
    
    
    def get_can_share(self, obj):
        # Only public posts are shareable
        return obj.visibility == 'public'
        fields = "__all__"