from django.urls import reverse
from service.tests import BaseAPITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Author


class AuthorViewTest(BaseAPITestCase):
    
    def setUp(self):
        super().setUp()
        
    # //service/api/authors/
    def test_author_list(self):
        """
        GET request to 'api/author/'
        Test that the author view returns a list of authors.
        """
        for i in range(3):
            self.user = User.objects.create_user(username=str(i), password='password')
            self.author = Author.objects.create(user=self.user, username=str(i), display_name='Test Author'+str(i))
        response = self.client.get(reverse('author-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
    
    # //service/api/authors/{AUTHOR_SERIAL}/
    def test_single_author(self):
        self.user = User.objects.create_user(username = "aa", password='password')
        self.author = Author.objects.create(user= "aa", username= "aa", display_name='Test Author'+str(i))
        response = self.client.get(reverse('author-detail', args=[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.serial == 1)
    
    # ://service/api/authors/{AUTHOR_FQID}/
    def get_author_fqid(self):
        self.user = User.objects.create_user(username = "aa", password='password')
        self.author = Author.objects.create(user= "aa", username= "aa", display_name='Test Author'+str(i))
        response = self.client.get(reverse('author-detail', args=[self.author.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.id == self.author.id)

