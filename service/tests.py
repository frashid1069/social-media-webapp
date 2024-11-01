from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Author, Post
from service import models


class PostViewTest(APITestCase):
    
    def setUp(self):
        # Create a user and an author
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.author = models.Author.objects.create(user=self.user, username='testauthor', display_name='Test Author')
        self.post = models.Post.objects.create(author=self.author, title="Test Post", visibility="public", is_deleted=False)
        self.client = APIClient()

    def test_post_creation(self):
        """
        Test that a post is created correctly.
        """
        self.client.force_authenticate(user=self.user)
        data = {
            'author': self.author.id,
            'title': 'New Post',
            'visibility': 'public'
        }
        response = self.client.post(reverse('post-list'), data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Post')

    def test_get_post_list(self):
        """
        Test getting a list of posts.
        """
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_filter_posts_by_author(self):
        """
        Test filtering posts by author ID.
        """
        response = self.client.get(reverse('post-list'), {'author_id': self.author.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

class LoginViewTest(APITestCase):

    def setUp(self):
        # Create a user and author for testing
        self.user = User.objects.create_user(username='testuser', password='password')
        self.author = models.Author.objects.create(user=self.user, username='testauthor', display_name='Test Author')

    def test_login_successful(self):
        """
        Test that login is successful with valid credentials.
        """
        data = {
            'username': 'testauthor',
            'password': 'password'
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_incorrect_password(self):
        """
        Test that login fails with an incorrect password.
        """
        data = {
            'username': 'testauthor',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class SignUpViewTest(APITestCase):

    def test_signup_success(self):
        """
        Test that signup is successful with valid data.
        """
        data = {
            'username': 'newuser',
            'display_name': 'New User',
            'password': 'password'
        }
        response = self.client.post(reverse('signup'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_signup_duplicate_username(self):
        """
        Test that signup fails with a duplicate username.
        """
        existing_user = User.objects.create_user(username='existinguser', password='password')
        models.Author.objects.create(user=existing_user, username='existinguser', display_name='Existing User')
        data = {
            'username': 'existinguser',
            'display_name': 'New User',
            'password': 'password'
        }
        response = self.client.post(reverse('signup'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class APITests(APITestCase):
   
    def setUp(self):

        # Create a test author
        self.author = Author.objects.create(
            user=User.objects.create_user(username="testauthor", password='1'),
            username="testauthor",
            display_name="Test Author",
            password='1',
        )
        
        # Create a test post
        self.post = Post.objects.create(
            author=self.author,
            title="Test Post",
            content="This is a test post",
            content_type="text/markdown"
        )

    def test_get_post_list(self):
        """
        Test getting the list of posts for a particular author
        URL: /api/post/?author_id=<id>
        """
        url = reverse('post-list')  # This will resolve to /api/post/
        response = self.client.get(url, {'author_id': self.author.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_author_list(self):
        """
        Test getting the list of authors
        URL: /api/author/
        """
        url = reverse('author-list')  # This will resolve to /api/author/
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_post(self):
        """
        Test getting a single post
        URL: /api/post/<id>/
        """
        url = reverse('post-detail', kwargs={'pk': self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.post.title)

    def test_create_post(self):
        """
        Test creating a post using POST request
        URL: /api/post/
        """
        url = reverse('post-list')
        data = {
            'author': self.author.id,
            'title': "New Test Post",
            'content': "This is a new test post",
            'content_type': "text/markdown"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_delete_post(self):
        """
        Test soft deleting a post
        URL: /api/post/<id>/
        """
        url = reverse('post-detail', kwargs={'pk': self.post.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify the post is marked as deleted
        self.post.refresh_from_db()
        self.assertTrue(self.post.is_deleted)

    def test_get_comment_list(self):
        """
        Test getting the list of comments for a post
        URL: /api/comment/?post_id=<id>
        """
        url = reverse('comment-list')
        response = self.client.get(url, {'post_id': self.post.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_likes(self):
        """
        Test getting the list of likes for a post
        URL: /api/like/?post_id=<id>
        """
        url = reverse('like-list')
        response = self.client.get(url, {'post_id': self.post.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_follow_list(self):
        """
        Test getting a list of followers or followees
        URL: /api/follow/?author_id=<id>
        """
        url = reverse('follow-list')
        response = self.client.get(url, {'author_id': self.author.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_inbox_list(self):
        """
        Test getting the list of inbox items for an author
        URL: /api/inbox/?author_id=<id>
        """
        url = reverse('inbox-list')
        response = self.client.get(url, {'author_id': self.author.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)