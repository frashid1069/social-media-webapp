from django.urls import reverse
from service.tests import BaseAPITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Author
from .serializers import AuthorSerializer

class AuthorViewTest(BaseAPITestCase):
    
    def setUp(self):
        super().setUp()
        
    # //service/api/authors/ test 
    def test_author_list(self):
        users = User.objects.all()
        authors = Author.objects.all()
        response = self.client.get(reverse('author-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["authors"]), len(authors))

    # //service/api/authors/{AUTHOR_SERIAL}/ Get
    def test_single_author(self):
        response = self.client.get(reverse('author-detail', args=[1]))
        author_serial = response.data["id"].split("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(author_serial[len(author_serial)-1], 1)
    
    # ://service/api/authors/{AUTHOR_FQID}/
    def test_author_fqid(self):
        fqid = self.client.get(reverse('author-detail', args=[1]))
        response = self.client.get(reverse('fqid-author-detail', args=[fqid.data["id"]]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["id"] == fqid.data["id"])
    
    # //service/api/authors/{AUTHOR_SERIAL}/ Put 
    def test_edit_profile(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"]) 
        response = self.client.put(reverse('author-detail', args=[1]), data={"displayName":"updated author"}, format="json")
        author1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(author1.display_name == "updated author")
