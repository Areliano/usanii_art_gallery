from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Aboutpage, Artists, Homepage, Artworks, Exhibitions, Contact, Footer, Customer, Moreartist

# Customizing User Admin to Allow Activation from Admin Panel
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Selected users have been approved.")
    approve_users.short_description = "Approve selected users"

# Unregister default User admin and register the customized one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Registering Other Models
admin.site.register(Aboutpage)
admin.site.register(Artists)
admin.site.register(Homepage)
admin.site.register(Artworks)
admin.site.register(Exhibitions)
admin.site.register(Contact)
admin.site.register(Footer)
admin.site.register(Customer)
admin.site.register(Moreartist)

# Customizing Django Admin Branding
admin.site.site_header = "Usanii Mashariki Administration"
admin.site.site_title = "Usanii Mashariki Panel"
admin.site.index_title = "Manage Art Gallery Data"
