from django.urls import path
from django.shortcuts import redirect
from . import views
from .views import send_inquiry_email
from .views import register, user_login, user_logout, activate, generate_reports
from .views import CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetCompleteView, \
    CustomPasswordResetConfirmView
from django.contrib.auth import views as auth_views
from .views import register, registration_success


# Redirect to login page when accessing the home page
def redirect_to_login(request):
    return redirect('login')


urlpatterns = [
    # Basic Redirects and Pages
    path('', redirect_to_login, name='home_redirect'),  # Redirects home to login
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('artists/', views.artists, name='artists'),
    path('moreartist/', views.moreartist, name='moreartist'),
    path('contact/', views.contact, name='contact'),
    path('artworks/', views.artworks, name='artworks'),

    # Exhibition Booking System
    path('exhibitions/', views.exhibitions, name='exhibitions'),
    path('book-exhibition/', views.book_exhibition, name='book_exhibition'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

    # Authentication Routes
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('registration-success/', registration_success, name='registration_success'),

    # Password Reset URLs
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Contact Form
    path('send-inquiry/', send_inquiry_email, name='send-inquiry'),


    # Report URLs ...
    path('admin/reports/', generate_reports, name='generate_reports'),
    path('admin/reports/data/', generate_reports, name='report_data'),  # For AJAX requests
]



