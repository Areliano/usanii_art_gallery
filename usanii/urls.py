from django.urls import path
from django.shortcuts import redirect
from . import views
from .views import send_inquiry_email
from .views import register, user_login, user_logout, activate

from .views import CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetCompleteView, CustomPasswordResetConfirmView
from .views import approve_customer, disapprove_customer
from django.contrib.auth import views as auth_views

# Redirect to login page when accessing the home page
def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('', redirect_to_login, name='home_redirect'),  # Redirects home to login
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('artists/', views.artists, name='artists'),
    path('moreartist/', views.moreartist, name='moreartist'),
    path('contact/', views.contact, name='contact'),
    path('artworks/', views.artworks, name='artworks'),
    path('reservation/', views.reservation, name='reservation'),
    path('booked/', views.booked, name='booked'),
    path('delete/<id>/', views.delete, name='delete'),
    path('insertdata/', views.insertdata, name='insertdata'),
    #path('edit/<id>/', views.edit, name='edit'),
    path('edit/<int:id>/', views.edit, name='edit'),

    path('send-inquiry/', send_inquiry_email, name='send-inquiry'),
    path('exhibitions/', views.exhibitions, name='exhibitions'),

    # Authentication Routes
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),

    # Password Reset URLs
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset-complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('approve_customer/<int:customer_id>/', approve_customer, name='approve_customer'),
    path('disapprove_customer/<int:customer_id>/', disapprove_customer, name='disapprove_customer'),



]
