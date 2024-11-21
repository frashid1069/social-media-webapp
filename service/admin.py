from django.contrib import admin
from . import models
from like.models import Like
from comment.models import Comment
from post.models import Post
# Register your models here.

admin.site.register(models.Author)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(models.Follow)
admin.site.register(models.Node)
