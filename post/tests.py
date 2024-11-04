from service.tests import BaseAPITestCase
from django.urls import reverse
from rest_framework import status
from .models import Post, Repost

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
    
    
# Below test cases made with the help of OpenAI. (2023). ChatGPT (GPT-3.5) "how to write test cases for an api in django python" 2024-11-03 
''' Below test cases made with the help of OpenAI. (2023). ChatGPT (GPT-3.5) "how to write to check this repost api:  " 2024-11-03  
    I included the api code for the repost in chatgpt aswell
'''         
class RepostViewTest(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(author=self.author1, title="Test Post", visibility="public")
        self.repost_url = reverse('repost-list')

    def test_create_repost_success(self):
        """
        Test successful repost creation.
        """
        data = {
            "post": self.post.id,
            "reposted_by": self.author2.id
        }
        response = self.client.post(self.repost_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['post'], self.post.id)
        self.assertEqual(response.data['reposted_by'], self.author2.id)

    def test_create_repost_missing_fields(self):
        """
        Test repost creation with missing fields.
        """
        data = {
            "post": self.post.id
        }
        response = self.client.post(self.repost_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Post and reposted_by fields are required.')

    def test_create_repost_nonexistent_post(self):
        """
        Test repost creation with a non-existent post.
        """
        data = {
            "post": 999,
            "reposted_by": self.author2.id
        }
        response = self.client.post(self.repost_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_create_repost_nonexistent_author(self):
        """
        Test repost creation with a non-existent author.
        """
        data = {
            "post": self.post.id,
            "reposted_by": 999
        }
        response = self.client.post(self.repost_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_delete_repost(self):
        """
        Test deleting a repost.
        """
        repost = Repost.objects.create(post=self.post, reposted_by=self.author2)
        delete_url = reverse('repost-detail', args=[repost.id])
        response = self.client.delete(delete_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Repost.objects.filter(id=repost.id).exists())