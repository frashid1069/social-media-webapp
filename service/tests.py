from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Author, Post, Like
from service import models

# class for set up testcase
class BaseAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.user1, self.author1 = self.create_test_user_and_author()
        self.user2, self.author2 = self.create_test_user_and_author()
        self.user3, self.author3 = self.create_test_user_and_author()
        # Login to obtain token and set credentials
        self.token = self.login_and_get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def create_test_user_and_author(self):
        users = User.objects.all()
        user = User.objects.create_user(username=f"testuser{len(users)}", password="password")
        author = Author.objects.create(user=user, username=f"testauthor{len(users)}", display_name=f"Test Author {len(users)}")
        return user, author

    def login_and_get_token(self):
        data = {
            'username': 'testauthor1',
            'password': 'password'
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data.get("token")

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

# Below test cases made with the help of OpenAI. (2023). ChatGPT (GPT-3.5) "how to write test cases for an api in django python" 2024-11-03  
class FollowViewTest(BaseAPITestCase):
    
    def setUp(self):
        super().setUp()
    
    def test_requestFollow(self):
        data = {
            "follower": "1",
            "followed": "2",
            "pending": "yes"
        }
        response = self.client.post(reverse("follow-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['follower'], 1)
        self.assertEqual(response.data['followed'], 2)

    def test_acceptFollow(self):
        data = {
            "follower": "1",
            "followed": "2",
            "pending": "yes"
        }
        response = self.client.post(reverse("follow-list"), data, format="json")

        data = {
            "follower": "1",
            "followed": "2",
            "pending": "no"
        }
        response = self.client.put(reverse("follow-detail", args=["1"]), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pending'], 'no')

    def test_declineFollow(self):
        data = {
            "follower": "1",
            "followed": "2",
            "pending": "yes"
        }
        response = self.client.post(reverse("follow-list"), data, format="json")
        response = self.client.delete(reverse("follow-detail", args=["1"]), format="json")
        self.assertEqual(response.status_code, 204)

    def test_unfollow(self):
        data = {
            "follower": "1",
            "followed": "2",
            "pending": "no"
        }
        response = self.client.post(reverse("follow-list"), data, format="json")
        response = self.client.delete(reverse("follow-detail", args=["1"]), format="json")
        self.assertEqual(response.status_code, 204)

class LikeViewTest(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        # Create a sample post for testing likes
        self.post = Post.objects.create(author=self.author1, title="Test Post", content="This is a test post.")

    def test_create_like(self):
        """
        Tests that a like can be created for a post by an author.
        """
        url = reverse("like-list")
        data = {
            "author": self.author1.id,
            "post": self.post.id
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(response.data["author"], self.author1.id)
        self.assertEqual(response.data["post"], self.post.id)