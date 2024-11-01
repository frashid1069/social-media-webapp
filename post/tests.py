from service.tests import BaseAPITestCase
from django.urls import reverse
from rest_framework import status
from .models import Post

class PostViewTest(BaseAPITestCase):
    '''        data = {
            'title': 'New Post',
            'author': self.author.id,
            'content': 'New content',
            "content_type": "text/markdown",
            'visibility': 'public'
        }'''
    def setUp(self):
        super().setUp()
        # Create a user and an author
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Post')
        
    def test_get_post_list(self):
        """
        GET request to '/api/post/'
        Test getting a list of posts.
        """
        for i in range(2):
            Post.objects.create(author=self.author, title="Test Post", visibility="public", is_deleted=False)
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_filter_posts_by_author(self):
        """
        GET request to '/api/post/?author_id=<pk>'
        Test filtering posts by author ID.
        """
        for i in range(2):
            Post.objects.create(author=self.author, title="Test Post", visibility="public", is_deleted=False)
            
        response = self.client.get(reverse('post-list'), {'author_id': self.author.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    # def test_filter_posts_by_visibility(self):
    #     """
    #     GET request to '/api/post/?author_id=<pk>'
    #     Test filtering posts by author ID.
    #     """