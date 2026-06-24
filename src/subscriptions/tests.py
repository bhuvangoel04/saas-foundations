from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Subscription

User = get_user_model()

class SubscriptionAPITests(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testapiuser',
            password='testpassword123',
            email='testapi@example.com'
        )
        # Create a subscription plan
        self.plan = Subscription.objects.create(
            name='Test Plan',
            subtitle='Test Subtitle',
            active=True,
            order=1
        )
        # Get or create token
        self.token = Token.objects.create(user=self.user)

    def test_get_subscription_plans(self):
        url = reverse('api_subscriptions_plans')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that our test plan is in the response
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Plan')

    def test_get_dashboard_unauthenticated(self):
        url = reverse('api_me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_get_dashboard_authenticated(self):
        url = reverse('api_me')
        # Authenticate using token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'testapiuser')
        self.assertEqual(response.data['subscription']['active'], True) # default status

    def test_update_profile(self):
        url = reverse('api_me')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {
            'first_name': 'API',
            'last_name': 'Tester',
            'email': 'updated@example.com'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'API')
        self.assertEqual(response.data['last_name'], 'Tester')
        self.assertEqual(response.data['email'], 'updated@example.com')
        
        # Verify db change
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'API')

    def test_obtain_token(self):
        url = reverse('api_token_auth')
        data = {
            'username': 'testapiuser',
            'password': 'testpassword123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['token'], self.token.key)

