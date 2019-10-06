
from django import forms

from .models import SignUp

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = SignUp
        fields = ['full_name', 'user_name', 'password', 'confirm_password', 'email', 'phone_number', 'current_location', 'work_location', 'user_type']
        # fields = ['full_name', 'user_name']
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # email_base, provider = email.split("@")
        # domain, extension = provider.split(".")
        # if not extension == "edu":
        #     raise forms.ValidationError("Please use a valid .EDU email address!")
        return email


    def clean_confirm_password(self):
        pass1 = self.cleaned_data.get('password')
        pass2 = self.cleaned_data.get('confirm_password')

        if pass1 != pass2:
            raise forms.ValidationError("The passwords entered do not match!")

        return pass2