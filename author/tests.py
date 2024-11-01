from django.urls import reverse
from service.tests import BaseAPITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Author


class AuthorViewTest(BaseAPITestCase):
    
    def setUp(self):
        super().setUp()
        

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

