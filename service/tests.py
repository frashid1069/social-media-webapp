from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from author.models import Author
from post.models import Post
from service import models
from .serializers import SignUpSerializer
from author.models import Author
# class for set up testcase
class BaseAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.user1, self.author1 = self.create_test_user_and_author("http://127.0.0.1:8000/")
        self.user2, self.author2 = self.create_test_user_and_author("http://127.0.0.1:8000/")
        self.user3, self.author3 = self.create_test_user_and_author("http://127.0.0.1:8000/")
        # Login to obtain token and set credentials
        self.token = self.login_and_get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def create_test_user_and_author(self, host):
        users = User.objects.all()
        user = User.objects.create_user(username=f"testuser{len(users)}", password="password")
        user.is_active = True
        user.save()
        validated_data = {"display_name":"test user", "bio":"bio", "github_url":"http://localhost:3000/home/signup"}
        author = Author.objects.create(user=user, host=f"{host}api", fqid=f"{host}api/authors/{user.id}", **validated_data)
        return user, author

    def login_and_get_token(self):
        data = {
            'username': 'testuser0',
            'password': 'password'
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data.get("token")

class LoginViewTest(BaseAPITestCase):

    def setUp(self):
        super().setUp()

    def test_login_successful(self):
        """
        Test that login is successful with valid credentials.
        """
        data = {
            'username': 'testuser0',
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
            'username': 'testuser0',
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
        data = {
            'username': 'testuser0',
            'password': 'password'
        }
        response = self.client.post(reverse('signup'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# Below test cases made with the help of OpenAI. (2023). ChatGPT (GPT-3.5) "how to write test cases for an api in django python" 2024-11-03  
class FollowViewTest(BaseAPITestCase):
    
    def setUp(self):
        super().setUp()
    
    # ://service/api/authors/{AUTHOR_SERIAL}/followers
    def test_get_followers(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author2 = self.client.get(reverse('author-detail', args=[2]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        author2 = Author.objects.get(fqid=author2.data["id"])
        follow = models.Follow.objects.create(follower=author2, followed=author1, pending="no")
        follows = models.Follow.objects.all()
        response = self.client.get(reverse('get_followers', args=[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["followers"]), len(follows))

    # ://service/api/authors/{AUTHOR_SERIAL}/followers/{FOREIGN_AUTHOR_FQID} Delete 
    def test_removefollower(self):
        self.test_get_followers()
        author2 = self.client.get(reverse('author-detail', args=[2]))
        author2 = Author.objects.get(fqid=author2.data["id"])
        response = self.client.delete(reverse('foreign_followers', args=[1, author2.fqid]))
        follows = models.Follow.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(follows))

    # ://service/api/authors/{AUTHOR_SERIAL}/followers/{FOREIGN_AUTHOR_FQID} Put 
    def test_acceptfollower(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author2 = self.client.get(reverse('author-detail', args=[2]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        author2 = Author.objects.get(fqid=author2.data["id"])
        follow = models.Follow.objects.create(follower=author2, followed=author1, pending="yes")
        response = self.client.put(reverse('foreign_followers', args=[1, author2.fqid]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        follow.refresh_from_db()
        self.assertEqual(follow.pending, "no")

    # # ://service/api/authors/{AUTHOR_SERIAL}/followers/{FOREIGN_AUTHOR_FQID} Get 
    def test_check_follower(self):
        self.test_get_followers()
        author2 = self.client.get(reverse('author-detail', args=[2]))
        author2 = Author.objects.get(fqid=author2.data["id"])
        response = self.client.get(reverse('foreign_followers', args=[1, author2.fqid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], author2.fqid)

    # ://service/api/authors/{AUTHOR_SERIAL}/inbox
    def test_requestFollow(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author2 = self.client.get(reverse('author-detail', args=[2]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        author2 = Author.objects.get(fqid=author2.data["id"])

        data = {"type":"follow", "actor":{"type":"author","id":author1.fqid}, "object":{"type":"author","id":author2.fqid}}
        response = self.client.post(reverse("inbox", args=[2]), data, format="json")
        follow = models.Follow.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(follow), 1)
 