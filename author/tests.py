from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Author


class AuthorViewTest(APITestCase):
    
    def setUp(self):
        # Set up test data, such as creating users and authors
        self.user = User.objects.create_user(username='testuser', password='password')
        self.author = Author.objects.create(user=self.user, username='testauthor', display_name='Test Author')

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

