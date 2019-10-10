
from django import forms

from .models import SignUp

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = SignUp
        fields = ['full_name', 'user_name', 'password', 'confirm_password', 'email', 'phone_number', 'current_location', 'work_location', 'user_type']

    def clean_user_name(self):
        new_user_name = self.cleaned_data.get('user_name')
        for old_user in SignUp.objects.all():
            if old_user.user_name == new_user_name:
                raise forms.ValidationError("The username entered already exists! Please try a different username.")

        return new_user_name


    def clean_confirm_password(self):
        pass1 = self.cleaned_data.get('password')
        pass2 = self.cleaned_data.get('confirm_password')

        if pass1 != pass2:
            raise forms.ValidationError("The passwords entered do not match!")

        return pass2

