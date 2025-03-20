
from django.urls import path

from . import views
from django.urls import path
from .views import send_inquiry_email

urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('artists', views.artists, name='artists'),
    path('moreartist/', views.moreartist, name='moreartist'),
    path('contact', views.contact, name='contact'),
    path('artworks', views.artworks, name='artworks'),
    path('reservation', views.reservation, name='reservation'),
    path('booked', views.booked, name='booked'),
    path('delete/<id>', views.delete, name='delete'),
    path('insertdata', views.insertdata, name='insertdata'),
    path('edit/<id>', views.edit, name='edit'),
    path('send-inquiry/', send_inquiry_email, name='send-inquiry'),
    path('exhibitions', views.exhibitions, name='exhibitions')


]