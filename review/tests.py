from django.test import TestCase
from .models import Review
from mainapp.models import SiteUser
from location.models import Location
from datetime import datetime


class ReviewModelTests(TestCase):
    def test_create_model(self):
        s1 = SiteUser.objects.create(full_name="test_user")
        l1 = Location.objects.create(state="NY")
        rev = Review.objects.create(
            location=l1, user=s1, content="test_content", time=datetime.now()
        )
        self.assertIsNotNone(rev)

    def test_add_review(self):
        s1 = SiteUser.objects.create(full_name="test_user")
        l1 = Location.objects.create(state="NY")
        r1 = Review.objects.create(
            location=l1, user=s1, content="test_content", time=datetime.now()
        )
        self.assertEqual(r1.content, "test_content")
