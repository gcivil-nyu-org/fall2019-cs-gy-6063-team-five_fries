from allauth.account.forms import SignupForm
from django import forms

# from django.contrib.auth.forms import UserChangeForm
from phonenumber_field.formfields import PhoneNumberField


class SiteUserSignupForm(SignupForm):
    email = forms.EmailField()
    full_name = forms.CharField(max_length=255, label="Full Name")
    current_location = forms.CharField(max_length=255, label="Current Location")
    work_location = forms.CharField(max_length=255, label="Work Location")
    phone_number = PhoneNumberField()

    def save(self, request):
        user = super(SiteUserSignupForm, self).save(request)
        user.full_name = self.cleaned_data.get("full_name")
        user.current_location = self.cleaned_data.get("current_location")
        user.work_location = self.cleaned_data.get("work_location")
        user.phone_number = self.cleaned_data.get("phone_number")
        user.save()
        return user
