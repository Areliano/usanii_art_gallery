from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils.html import format_html
from .models import (
    Aboutpage, Artists, Homepage, Artworks, Exhibitions,
    Contact, Footer, Customer, Moreartist, Reservation
)

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
admin.site.register(Moreartist)

# Customizing Customer Admin for Approval Actions
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'event', 'is_approved', 'approval_links')

    def approval_links(self, obj):
        approve_url = reverse('approve_customer', args=[obj.id])
        disapprove_url = reverse('disapprove_customer', args=[obj.id])

        if obj.is_approved is None:
            return format_html(
                '<a style="color:green; text-decoration:none;" href="{}">Approve</a> | '
                '<a style="color:red; text-decoration:none;" href="{}">Disapprove</a>',
                approve_url, disapprove_url
            )
        elif obj.is_approved:
            return format_html('<span style="color:green;">✔ Approved</span>')
        else:
            return format_html('<span style="color:red;">✖ Disapproved</span>')

    approval_links.short_description = 'Approval Actions'

# ✅ Directly Register Customer (Removed Unregister)
admin.site.register(Customer, CustomerAdmin)

# Customizing Django Admin Branding
admin.site.site_header = "Usanii Mashariki Administration"
admin.site.site_title = "Usanii Mashariki Panel"
admin.site.index_title = "Manage Art Gallery Data"
