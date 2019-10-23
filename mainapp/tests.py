from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from bs4 import BeautifulSoup


class BaseTemplateTestCase(TestCase):
    def setUp(self):
        pass

    def test_my_account_on_header(self):
        """If a user has been logged in, My Account should be shown in the header"""
        self.client = Client()
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        response = self.client.get(reverse("index"))
        soup = BeautifulSoup(response.content, "html.parser")
        nav = soup.find("nav", class_="navbar")
        self.assertIn("My Account", nav.text)

    def test_log_in_on_header(self):
        """If a user has not been logged in, Log In should be shown in the header"""
        self.client = Client()
        response = self.client.get(reverse("index"))
        soup = BeautifulSoup(response.content, "html.parser")
        nav = soup.find("nav", class_="navbar")
        self.assertIn("Log In", nav.text)
