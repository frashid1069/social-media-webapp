from django.urls import reverse
from service.tests import BaseAPITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Comment, Post

class CommentViewTest(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(author=self.author, title="Test Post", visibility="public", is_deleted=False)

    def test_comment_creation(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'content': 'New comment',
            'author': self.author.user.id,
            "post": self.post.id,
        }
        response = self.client.post(reverse('comment-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'New comment')
    
    def test_get_comment_list(self):
        Comment.objects.create(author=self.author, content="Test Comment", post=self.post)
        response = self.client.get(reverse('comment-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
