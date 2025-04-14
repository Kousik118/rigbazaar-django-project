from django.test import TestCase, Client
from django.urls import reverse
from .models import Account, Product
class BasicViewTests(TestCase):

    def setUp(self):
        self.user = Account.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.client = Client()

    def test_home_view_anonymous(self):
        """Test home view redirects anonymous users to login."""
        response = self.client.get(reverse('app1:home'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('app1:login') + '?next=' + reverse('app1:home'))

    def test_home_view_logged_in(self):
        """Test home view for logged-in user."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('app1:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome, testuser")
        self.assertTemplateUsed(response, 'home.html')

    def test_login_view_get(self):
        """Test login page loads correctly."""
        response = self.client.get(reverse('app1:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertContains(response, "Login")

    def test_reg_view_get(self):
        """Test registration page loads correctly."""
        response = self.client.get(reverse('app1:reg'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reg.html')
        self.assertContains(response, "Create Account")