from django.db import models
from django.utils import timezone
from author.models import Author


class Node(models.Model):
    name = models.CharField(max_length=20, editable = True, blank=True, null=True)
    url = models.URLField(max_length = 100, editable = True)
    username = models.CharField(max_length=20, editable = True, blank=True, null=True)
    password = models.CharField(max_length=20, editable = True, blank=True, null=True)
    is_allowed = models.BooleanField(default = False)
    
    def __str__(self):
        return str(self.name)

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
    
    def accept(self):
        """
        Set the pending status to 'no' to activate the follow relationship.
        """
        self.pending = 'no'
        self.save(update_fields=['pending'])

    def reject(self):
        """
        Reject the follow request by deleting the object.
        """
        self.delete()
    
    @property
    def is_active(self):
        """
        Returns True if the follow relationship is active (pending = 'no').
        """
        return self.pending == 'no'
    
class FollowManager(models.Manager):
    def active(self):
        """
        Returns all active follow relationships (pending = 'no').
        """
        return self.filter(pending='no')
    


    
