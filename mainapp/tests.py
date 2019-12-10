from django.test import TestCase
from django.urls import reverse

from location.models import Location, Apartment
from review.models import Review
from .models import SiteUser
from bs4 import BeautifulSoup


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

    def test_favorites_on_header(self):
        """If a user has been logged in, Favorites should be shown in the header"""
        self.client.force_login(SiteUser.objects.create(username="testuser"))
        response = self.client.get(reverse("index"))
        soup = BeautifulSoup(response.content, "html.parser")
        nav = soup.find("nav", class_="navbar")
        self.assertIn("Favorites", nav.text)


class AccountViewTestCase(TestCase):
    def test_redirect_user_if_not_logged_in(self):
        response = self.client.get(reverse("account"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/?next=/account")

    def test_show_account_view_if_logged_in(self):
        self.client.force_login(SiteUser.objects.get_or_create(username="testuser")[0])
        response = self.client.get(reverse("account"))
        self.assertEqual(response.status_code, 200)

    def test_show_review_view(self):
        s1 = SiteUser.objects.create(full_name="test_user")
        l1 = Location.objects.create(state="NY")
        r1 = Review.objects.create(location=l1, user=s1, content="test_content")
        self.client.force_login(
            SiteUser.objects.get_or_create(full_name="test_user")[0]
        )
        response = self.client.get(reverse("account"))
        self.assertContains(response, r1.content)

    def test_show_landlord_apartments(self):
        city = "Brooklyn"
        state = "New York"
        address = "1234 Coney Island Avenue"
        zipcode = 11218
        # using get_or_create avoids race condition
        loc = Location.objects.get_or_create(
            city=city, state=state, address=address, zipcode=zipcode
        )[0]

        # create an apartment and link it to that location
        suite_num = "18C"
        number_of_bed = 3
        image = "Images/System_Data_Flow_Diagram.png"
        rent_price = 3000
        apt = Apartment.objects.create(
            suite_num=suite_num,
            number_of_bed=number_of_bed,
            image=image,
            rent_price=rent_price,
            location=loc,
        )

        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        apt.landlord = user
        apt.save()
        response = self.client.get(reverse("account"))
        soup = BeautifulSoup(response.content, "html.parser")
        content = soup.get_text()
        self.assertIn(apt.suite_num, content)
        self.assertIn(str(apt.rent_price), content)
        self.assertIn(str(apt.number_of_bed), content)


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
