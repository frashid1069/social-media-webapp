from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Author, Post
from service import models

# class for set up testcase
class BaseAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.user, self.author = self.create_test_user_and_author()

        # Login to obtain token and set credentials
        self.token = self.login_and_get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def create_test_user_and_author(self):
        user = User.objects.create_user(username="testuser", password="password")
        author = Author.objects.create(user=user, username="testauthor", display_name="Test Author")
        return user, author

    def login_and_get_token(self):
        data = {
            'username': 'testauthor',
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


