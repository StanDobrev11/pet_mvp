from django.test import TestCase
from django.urls import reverse
from django.contrib.sites.models import Site

class GoogleLoginTest(TestCase):
    def setUp(self):
        Site.objects.update_or_create(id=1, defaults={'domain': 'localhost:8000', 'name': 'localhost'})

    def test_index_page_has_google_button(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Sign in with Google')

    def test_google_login_redirect(self):
        url = reverse('google_login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('https://accounts.google.com', response.url)

