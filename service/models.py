from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from author.models import Author
from post.models import Post, Repost
from comment.models import Comment

# Create your models here.

# class Like(models.Model):
#     author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='likes')
#     post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    
#     created_at = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"Like by {self.author} on {self.post}"

class Node(models.Model):
    url = models.URLField(max_length = 100, editable = True)
    is_allowed = models.BooleanField(default = False)

class Follow(models.Model):
    '''Follower.objects.create(follower=author1, followed=author2) 
    => author1 follows author2
    authors_followed_by_author1 = author1.following.all() Returns [author2]
    followers_of_author2 = author2.followers.all()  # Returns [author1]'''
    
    # related_name='following' allows you to get all the authors that a particular author is following.
    follower = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='following')
    
    # related_name='followers' allows you to get all the users who follow a particular Author via this ForeignKey
    followed = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='followers')
    
    PENDING_CHOICES = [('yes', 'Yes'), ('no', 'No')]
    pending = models.CharField(max_length=10, choices=PENDING_CHOICES, default='yes')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.follower} follows {self.followed}"
    
    def get_follower(self):
        return self.follower
    

# Inbox Model
# class Inbox(models.Model):
#     author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='inbox')
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#     comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
#     like = models.ForeignKey(Like, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"Inbox for {self.author}"
    
    
