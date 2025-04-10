from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils.html import format_html
from .models import (
    Aboutpage, Artists, Homepage, Artworks, Exhibition,
    Contact, Footer, Moreartist, Booking
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


# Exhibition Admin with Booking Count
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'start_time', 'end_time', 'max_capacity', 'bookings_count', 'available_spots')
    readonly_fields = ('bookings_count', 'available_spots')

    def bookings_count(self, obj):
        return Booking.objects.filter(exhibition=obj).count()

    bookings_count.short_description = 'Bookings'

    def available_spots(self, obj):
        return obj.max_capacity - Booking.objects.filter(exhibition=obj).count()

    available_spots.short_description = 'Available Spots'


# Booking Admin with Custom Actions
class BookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'exhibition', 'booking_date', 'is_confirmed', 'confirmation_actions')
    list_filter = ('is_confirmed', 'exhibition')
    search_fields = ('name', 'email', 'exhibition__title')
    actions = ['confirm_bookings', 'cancel_bookings']

    def confirmation_actions(self, obj):
        if obj.is_confirmed:
            return format_html('<span style="color:green;">✔ Confirmed</span>')
        return format_html(
            '<a class="button" href="{}">Confirm</a>',
            reverse('admin:confirm_booking', args=[obj.pk])
        )

    confirmation_actions.short_description = 'Actions'

    def confirm_bookings(self, request, queryset):
        queryset.update(is_confirmed=True)
        self.message_user(request, "Selected bookings have been confirmed.")

    confirm_bookings.short_description = "Confirm selected bookings"

    def cancel_bookings(self, request, queryset):
        queryset.delete()
        self.message_user(request, "Selected bookings have been cancelled.")

    cancel_bookings.short_description = "Cancel selected bookings"


from django import forms
from django.contrib import admin
from .models import Exhibition


class ExhibitionAdminForm(forms.ModelForm):
    class Meta:
        model = Exhibition
        fields = '__all__'
        widgets = {
            'start_time': forms.TimeInput(format='%H:%M', attrs={'placeholder': 'HH:MM'}),
            'end_time': forms.TimeInput(format='%H:%M', attrs={'placeholder': 'HH:MM'}),
        }


class ExhibitionAdmin(admin.ModelAdmin):
    form = ExhibitionAdminForm
    list_display = ('title', 'date', 'start_time', 'end_time', 'available_spots')

    def available_spots(self, obj):
        return obj.available_spots()

    available_spots.short_description = 'Available Spots'


admin.site.register(Exhibition, ExhibitionAdmin)

# Registering Models with Custom Admin Classes
#admin.site.register(Exhibition, ExhibitionAdmin)
admin.site.register(Booking, BookingAdmin)

# Registering Other Models with Default Admin
admin.site.register(Aboutpage)
admin.site.register(Artists)
admin.site.register(Homepage)
admin.site.register(Artworks)
admin.site.register(Contact)
admin.site.register(Footer)
admin.site.register(Moreartist)

# Customizing Django Admin Branding
admin.site.site_header = "Usanii Mashariki Administration"
admin.site.site_title = "Usanii Mashariki Panel"
admin.site.index_title = "Manage Art Gallery Data"