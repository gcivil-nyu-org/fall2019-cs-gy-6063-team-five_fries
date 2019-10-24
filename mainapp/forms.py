from .models import SiteUser
from allauth.account.forms import SignupForm
from django import forms

# from django.contrib.auth.forms import UserChangeForm
from phonenumber_field.formfields import PhoneNumberField


class SiteUserSignupForm(SignupForm):
    full_name = forms.CharField(max_length=255, label="Full Name")
    current_location = forms.CharField(max_length=255, label="Current Location")
    work_location = forms.CharField(max_length=255, label="Work Location")
    phone_number = PhoneNumberField()
    user_type = forms.ChoiceField(
        choices=tuple([(k, v) for k, v in SiteUser.user_type_string_map.items()]),
        label="Type",
    )
    email = forms.EmailField()

    def save(self, request):
        user = super(SiteUserSignupForm, self).save(request)
        user.full_name = self.cleaned_data.get("full_name")
        user.current_location = self.cleaned_data.get("current_location")
        user.work_location = self.cleaned_data.get("work_location")
        user.phone_number = self.cleaned_data.get("phone_number")
        user.user_type = self.cleaned_data.get("user_type")
        user.save()
        return user
