from django.test import TestCase
from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from rest_framework import status
from django.contrib.auth.models import User
from author.models import Author
from .models import Post
from .views import PostView
from django.urls import reverse

class PostViewTest(APITestCase):
    '''        data = {
            'title': 'New Post',
            'author': self.author.id,
            'content': 'New content',
            "content_type": "text/markdown",
            'visibility': 'public'
        }'''
    def setUp(self):
        # Create a user and an author
        self.user = User.objects.create_user(username='testuser', password='password')
        self.author = Author.objects.create(user=self.user, username='testauthor', display_name='Test Author')
        self.post = Post.objects.create(author=self.author, title="Test Post", visibility="public", is_deleted=False)
        
    
    def test_post_creation(self):
        """
        POST request to '/api/post/'
        Test that a post is created correctly.
        """
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Post',
            'author': self.author.user.id,
            'content': 'New content',
            "content_type": "text/markdown",
        }
        response = self.client.post(reverse('post-list'), data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Post')
    # def test_get_post_list(self):
    #     """
    #     Test getting a list of posts.
    #     """
    #     response = self.client.get(reverse('post-list'))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertTrue(len(response.data) > 0)

    # def test_filter_posts_by_author(self):
    #     """
    #     Test filtering posts by author ID.
    #     """
    #     response = self.client.get(reverse('post-list'), {'author_id': self.author.id})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertTrue(len(response.data) > 0)

