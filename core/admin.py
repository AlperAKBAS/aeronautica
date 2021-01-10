from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.models import Profile, User
from .forms import UserAdminCreationForm, UserAdminChangeForm


class UserAdminEdited(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    ordering = ['id']
    list_display = ['email', 'first_name', 'last_name', 'is_admin', 'is_staff']
    list_filter = ['email', 'first_name', 'last_name', 'is_admin', 'is_staff', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    
    # Update User
    fieldsets = (
                        (None, {'fields': ('email', 'password')}),
                        (_('Personal Info'), 
                            {'fields': (
                                'first_name',
                                'last_name',
                                )}),
                        (
                            _('Permissions'),
                            {
                                'fields': (
                                    'is_active',
                                    'is_staff',
                                    'is_superuser',
                                    'is_demo_user',
                                    'is_admin',
                                )
                            }
                        ),
                        (_('Important dates'), {'fields': ('last_login',)}),
                    )

    # Add User
    add_fieldsets = (
                        (None, { # header
                            'classes': ('wide',), # css classes
                            'fields': (
                                'email', 
                                'password1', 
                                'password2', 
                                'first_name',
                                'last_name',
                                )
                        }),
                    )

class ProfileAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = ['user', 'full_name', 'title', 'company', 'position']
    list_filter = ['company']


admin.site.register(User, UserAdminEdited)
admin.site.register(Profile, ProfileAdmin)
admin.site.unregister(Group)
