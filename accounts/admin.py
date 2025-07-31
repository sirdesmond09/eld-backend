from core.models import User
from django.contrib import admin
from django.utils.html import format_html


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "display_picture",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("is_staff", "is_active", "date_joined")
    ordering = ("-date_joined",)
    list_display_links = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
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
    readonly_fields = (
        "last_login",
        "date_joined",
    )
    filter_horizontal = ("groups", "user_permissions")
    list_per_page = 20
    actions = [
        "activate_users",
        "deactivate_users",
    ]

    def name(self, obj):
        return obj.get_full_name()

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Selected users have been activated.")

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Selected users have been deactivated.")

    def display_picture(self, obj):
        if not obj.avatar:
            return None
        return format_html(
            '<img src="{}" width="50" height="50"/>'.format(obj.avatar.url)
        )

    display_picture.short_description = "Profile Picture" 