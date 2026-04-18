from django.contrib import admin
from .models import ElUser
from django.contrib.auth.admin import UserAdmin


class ElUserAdmin(UserAdmin):
    # a list of fields to be displayed in the list view of the admin page
    list_display = (
        "username",
        "nickname",
        "phone",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    # a list of fields to be used for searching in the admin page
    search_fields = ("username", "phone", "nickname")
    # a list of fields that can be used to filter the results in the admin page
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")

    # a tuple of fields to be used for editing an existing user
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "nickname",
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "avatar",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )


admin.site.register(ElUser, ElUserAdmin)
