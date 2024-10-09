from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from .models import *

# Create your tests here.
factory = APIRequestFactory()

class UserAPITest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='userA@gmail.com', first_name="Annie", last_name="Kelly", password='password123')

    def test_register(self):
        url = reverse('register')
        data = {"email": "test4@gmail.com",
		"password" : "password555",
    "first_name": "Darnold",
    "last_name": "Danderson"
    }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login(self):
        url = reverse('token_obtain_pair')
        data = {"email":"userA@gmail.com", "password":"password123" }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)


class ProductAPITest(APITestCase):
    def setUp(self):
        self.product = Product.objects.create(name='test_product', description ='a test listing', price="9.99", stock_number="1")

    def test_get_products(self):
        url = reverse('products')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "test_product")


class CartAPITest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='userA@gmail.com', first_name="Annie", last_name="Kelly", password='password123')
        self.product = Product.objects.create(name='test_product', description ='a test listing', price="9.99", stock_number="1")

    def test_get_cart(self):
        url = reverse('view_add_cart', kwargs={'pk':"1"})
        response = self.client.get(url)
        print(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertIn('owner', response.data)

