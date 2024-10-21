from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from service import models

class AuthorViewTest(APITestCase):
    
    def setUp(self):
        # Set up test data, such as creating users and authors
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.author = models.Author.objects.create(user=self.user, username='testauthor', display_name='Test Author')
        self.client = APIClient()

    def test_author_creation(self):
        """
        Test that the author view creates an author.
        """
        data = {
            'username': 'newauthor',
            'display_name': 'New Author',
            'password': 'newpassword'
        }
        response = self.client.post(reverse('author-list'), data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newauthor')

    def test_author_list(self):
        """
        Test that the author view returns a list of authors.
        """
        response = self.client.get(reverse('author-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

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
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.author = models.Author.objects.create(user=self.user, username='testauthor', display_name='Test Author', password='testpass')
        self.client = APIClient()

    def test_login_successful(self):
        """
        Test that login is successful with valid credentials.
        """
        data = {
            'username': 'testauthor',
            'password': 'testpass'
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

    def setUp(self):
        self.client = APIClient()

    def test_signup_success(self):
        """
        Test that signup is successful with valid data.
        """
        data = {
            'username': 'newuser',
            'display_name': 'New User',
            'password': 'newpassword'
        }
        response = self.client.post(reverse('signup'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_signup_duplicate_username(self):
        """
        Test that signup fails with a duplicate username.
        """
        existing_user = User.objects.create_user(username='existinguser', password='password123')
        models.Author.objects.create(user=existing_user, username='existinguser', display_name='Existing User')
        data = {
            'username': 'existinguser',
            'display_name': 'New User',
            'password': 'newpassword'
        }
        response = self.client.post(reverse('signup'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



