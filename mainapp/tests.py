from django.test import TestCase
from django.urls import reverse

# from django.contrib.auth.models import User
from .models import SiteUser
from bs4 import BeautifulSoup


# def create_site_user()


class BaseTemplateTestCase(TestCase):
    def setUp(self):
        pass

    def test_my_account_on_header(self):
        """If a user has been logged in, My Account should be shown in the header"""
        self.client.force_login(SiteUser.objects.get_or_create(username="testuser")[0])
        response = self.client.get(reverse("index"))
        soup = BeautifulSoup(response.content, "html.parser")
        nav = soup.find("nav", class_="navbar")
        self.assertIn("My Account", nav.text)

    def test_log_in_on_header(self):
        """If a user has not been logged in, Log In should be shown in the header"""
        response = self.client.get(reverse("index"))
        soup = BeautifulSoup(response.content, "html.parser")
        nav = soup.find("nav", class_="navbar")
        self.assertIn("Log In", nav.text)


"""
class LoginViewTestCase(TestCase):
    def test_get_login_view(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        username = "username"
        password = "password"

        SiteUser.objects.create_user(username, password=password)
        response = self.client.post(
            reverse("account_login"), {"username": username, "password": password}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

    def test_login_failure(self):
        response = self.client.post(
            reverse("account_login"), {"username": "invalid", "password": "invalid"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login")
"""
"""
class AccountViewTestCase(TestCase):
    def test_redirect_user_if_not_logged_in(self):
        response = self.client.get(reverse("account"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login")

    def test_show_account_view_if_logged_in(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        response = self.client.get(reverse("account"))
        self.assertEqual(response.status_code, 200)
"""


class MainIndexViewTestCase(TestCase):
    def test_main_index_view(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)


class SiteUserModelTests(TestCase):
    def test_string(self):
        """
        test the __str__ method to insure it returns the
        correct value
        """
        user = SiteUser.objects.create(username="test_user")
        self.assertEqual("test_user", str(user))

    def test_user_type_renter(self):
        """
        tests whether a user created with the "Renter" type
        returns the correct value from its get_user_type method
        """
        user = SiteUser.objects.create(user_type="R", username="test_user")
        self.assertEqual("Renter", user.user_type_string())

    def test_user_type_tenant(self):
        """
        tests whether a user created with the "Renter" type
        returns the correct value from its get_user_type method
        """
        user = SiteUser.objects.create(user_type="T", username="test_user")
        self.assertEqual("Tenant", user.user_type_string())

    def test_user_type_landlord(self):
        """
        tests whether a user created with the "Renter" type
        returns the correct value from its get_user_type method
        """
        user = SiteUser.objects.create(user_type="L", username="test_user")
        self.assertEqual("Landlord", user.user_type_string())
