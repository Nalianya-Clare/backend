from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from .models import User, LoggedInUser


# Register your models here.
class CustomAdminSite(admin.AdminSite, admin.ModelAdmin):
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True

admin_site = CustomAdminSite(name='customadmin')


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    list_display = ("email", "first_name", "last_name", "phone", "gender", "profile_picture", "is_staff",
                    "is_active", "verified", "meeting_url", "is_medical_staff", "is_approved_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    readonly_fields = ['date_joined', 'last_login']
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone", "gender",'meeting_url')}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    'is_medical_staff',
                    'is_approved_staff',
                    "groups",
                    "user_permissions",
                    "verified",
                    "role",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs


@admin.register(LoggedInUser)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("user", "session_key", "refresh_token")
    search_fields = ("id",)
    ordering = ("-id",)
