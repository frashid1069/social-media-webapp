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
    description = serializers.CharField(required=True)
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
        
    
    # def get_likes(self, obj):
    #     likes = Like.objects.filter(object=obj.fqid)
    #     return {
    #         "type": "comments",
    #         "id": "http://nodebbbb/api/authors/222/posts/293/comments",
    #         "page": "http://nodebbbb/authors/222/posts/293/comments",
    #         "page_number": 1,
    #         "size": 5,
    #         "count": len(likes),
    #         "src": LikeSerializer(likes, many=True).data,
    #     }
        
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
        comments_queryset = Comment.objects.filter(post=obj.id)
        paginator = CommentPagination()
        request = self.context.get('request', None)
        page = paginator.paginate_queryset(comments_queryset, request, view=None)

        url = self.context['request'].build_absolute_uri().strip('/')
        paginated_response = paginator.get_paginated_response(
            CommentSerializer(page, many=True).data,
            url=url
        )
        return paginated_response.data
    
    # def get_comments(self, obj):
    #     comments = Comment.objects.filter(post=obj.id)
    #     if not comments.exists():
    #         return {}
    #     return CommentSerializer(comments, many=True).data
    
    def validate_visibility(self, value):
        # Normalize value to lowercase and ensure it matches a valid choice
        normalized_value = value.lower()
        valid_choices = [choice[0] for choice in Post.VISIBILITY_CHOICES]
        if normalized_value not in valid_choices:
            raise serializers.ValidationError(f"Invalid visibility value: {value}")
        return normalized_value
    
    # def create(self, validated_data):
    #     comments_data = validated_data.pop('comments', {})
    #     post = super().create(validated_data)

    #     # Create associated comments if provided
    #     for comment_data in comments_data:
    #         author_data = comment_data.pop('author', {})
    #         author_fqid = author_data.get('id')
    #         if Author.objects.filter(fqid=author_fqid).exists():
    #             comment_author = Author.objects.get(fqid=author_fqid)
    #         else:
    #             serializer = AuthorSerializer(data=author_data)
    #             if serializer.is_valid():
    #                 comment_author = serializer.save(fqid=author_fqid)
                    
    #                 print(f"Author copy created successfully: {comment_author.display_name} (fqid: {comment_author.fqid})")

    #         Comment.objects.create(author=comment_author, post=post, fqid=comment_data.get('id'), **comment_data)

    #     return post

    # def update(self, instance, validated_data):
    #     comments_data = validated_data.pop('comments', {})
    #     post = super().update(instance, validated_data)

    #     # Update or create associated comments
    #     for comment_data in comments_data:
    #         author_data = comment_data.pop('author', {})
    #         author_fqid = author_data.get('id')
            
    #         # check if author exists, create copy if not
    #         if Author.objects.filter(fqid=author_fqid).exists():
    #             comment_author = Author.objects.get(fqid=author_fqid)
    #         else:
    #             serializer = AuthorSerializer(data=author_data)
    #             if serializer.is_valid():
    #                 comment_author = serializer.save(fqid=author_fqid)
                    
    #                 print(f"Author copy created successfully: {comment_author.display_name} (fqid: {comment_author.fqid})")
            
    #         # check if comment exists, create copy if not
    #         comment_fqid = comment_data.get('id')
    #         if Comment.objects.filter(post=post, fqid=comment_fqid).exists():
    #             comment = Comment.objects.get(fqid=comment_fqid)
    #             serializer = CommentSerializer(comment, data=comment_data, partial=True)
    #             if serializer.is_valid():
    #                 serializer.save()
    #         else:
    #             serializer = CommentSerializer(data=comment_data)
    #             if serializer.is_valid():
    #                 serializer.save(author=comment_author, post=post, fqid=comment_fqid)

    #     return post
        
    

    def get_can_share(self, obj):
        # Only public posts are shareable
        return obj.visibility == 'public'
        fields = "__all__"