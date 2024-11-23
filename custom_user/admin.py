"""Integrate CustomUser app with Django admin."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Profile, User


class ProfileInline(admin.StackedInline):
    """Define the Profile inline admin integration."""

    model = Profile


class UserAdmin(DjangoUserAdmin):
    """Define User admin integration."""

    inlines = [ProfileInline]
    readonly_fields = ["country"]
    list_display = [*DjangoUserAdmin.list_display, "country"]
    list_filter = [*DjangoUserAdmin.list_filter, "profile__accept_terms"]
    fieldsets = [*DjangoUserAdmin.fieldsets, (_("MegaRed"), {"fields": ["country"]})]

    def get_inline_instances(self, request, obj=None):
        """Disable inlines for new Users."""
        if not obj:
            return []

        return super().get_inline_instances(request, obj=None)

    def get_readonly_fields(self, request, obj=None):
        """Exclude username for MegaRed users."""
        if obj and obj.is_megared:
            readonly_fields = self.readonly_fields or []
            return [*readonly_fields, "username", "first_name", "last_name", "email"]

        return self.readonly_fields


admin.site.register(User, UserAdmin)
