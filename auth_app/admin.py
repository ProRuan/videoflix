# Third-party suppliers
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy

# Local imports
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Represents a user admin.
    """
    ordering = ['email']
    search_fields = ['email']
    list_display = ['email', 'is_staff', 'is_superuser']
    readonly_fields = ['last_login', 'date_joined']

    fieldsets = (
        (
            None,
            {'fields': ('email', 'password')}
        ),
        (
            gettext_lazy('Personal info'),
            {'fields': ('username', 'first_name', 'last_name')}
        ),
        (
            gettext_lazy('Permissions'),
            {
                'fields': (
                    'is_active', 'is_staff', 'is_superuser',
                    'groups', 'user_permissions'
                )
            }
        ),
        (
            gettext_lazy('Important dates'),
            {'fields': ('last_login', 'date_joined')}
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2'),
            }
        ),
    )
