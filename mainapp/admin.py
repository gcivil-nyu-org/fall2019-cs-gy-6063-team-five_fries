from django.contrib import admin

from signup.forms import SignUpForm
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["__str__", "timestamp", "updated"]
    form = SignUpForm


admin.site.register(Profile, ProfileAdmin)
