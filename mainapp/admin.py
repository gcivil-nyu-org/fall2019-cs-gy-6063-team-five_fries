from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import SiteUser


class SiteUserAdmin(UserAdmin):
    list_display = ["username", "email", "updated"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    # "id",
                    "first_name",
                    "last_name",
                    "phone_number",
                    "current_location",
                    "work_location",
                )
            },
        ),
    )

    class Meta:
        model = SiteUser


admin.site.register(SiteUser, SiteUserAdmin)
