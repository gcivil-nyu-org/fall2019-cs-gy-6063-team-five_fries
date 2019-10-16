from django import forms

from mainapp.models import Profile
from django.contrib.auth.models import User


class SignUpForm(forms.ModelForm):
    username = forms.CharField(max_length=150, strip=True)
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=150)

    class Meta:
        model = Profile
        fields = [
            "username",
            "password",
            "confirm_password",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "current_location",
            "work_location",
            "user_type",
        ]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(
            "The username entered already exists! Please try a different username."
        )

    def clean_confirm_password(self):
        pass1 = self.cleaned_data.get("password")
        pass2 = self.cleaned_data.get("confirm_password")

        if pass1 != pass2:
            raise forms.ValidationError("The passwords entered do not match!")

        return pass2

    # https://stackoverflow.com/a/13550897
    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"],
            email=self.cleaned_data["email"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )

        user.profile.phone_number = self.cleaned_data["phone_number"]
        user.profile.current_location = self.cleaned_data["current_location"]
        user.profile.work_location = self.cleaned_data["work_location"]
        user.profile.user_type = self.cleaned_data["user_type"]

        if commit:
            user.save()
        return user
