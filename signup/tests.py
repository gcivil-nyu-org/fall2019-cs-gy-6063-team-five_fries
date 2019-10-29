from django.test import TestCase
from .forms import SignUpForm
from django.contrib.auth.models import User


class SignUpFormTests(TestCase):
    valid_form_data = {
        "username": "ABC",
        "password": "password",
        "confirm_password": "password",
        "email": "abc@gmail.com",
        "first_name": "First",
        "last_name": "Last",
        "phone_number": "+13475742125",
        "current_location": "Brooklyn, NY",
        "work_location": "Brooklyn, NY",
        "user_type": "R",
    }

    def test_valid(self):
        form = SignUpForm(data=SignUpFormTests.valid_form_data)
        self.assertTrue(form.is_valid())

    def test_wrong_password_confirm(self):
        form_data = SignUpFormTests.valid_form_data
        form_data["confirm_password"] = "asdf"
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_wrong_user_type(self):
        form_data = SignUpFormTests.valid_form_data
        form_data["user_type"] = "Z"
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_wrong_phone_number(self):
        form_data = SignUpFormTests.valid_form_data
        form_data["phone_number"] = "3475742125"
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_existing_user(self):
        form_data = SignUpFormTests.valid_form_data
        User.objects.create_user(username=form_data["username"])
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_save(self):
        form_data = SignUpFormTests.valid_form_data
        form = SignUpForm(data=form_data)
        form.full_clean()

        form.save()

        try:
            User.objects.get(username=form_data["username"])
        except User.DoesNotExist:
            self.fail("SignUpForm.save() has failed to create a user")
