from django.contrib import admin
from . import models
from like.models import Like
# Register your models here.

admin.site.register(models.Author)
admin.site.register(models.Post)
admin.site.register(models.Comment)
admin.site.register(Like)
admin.site.register(models.Follow)
admin.site.register(models.Node)
