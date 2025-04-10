from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from .models import Aboutpage, Artists, Homepage, Artworks, Exhibition, Contact, Footer, Moreartist, Booking
from django.http import JsonResponse
from datetime import datetime
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.views.decorators.http import require_POST
import json


# User Registration with Admin Approval
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User remains inactive until approved
            user.save()
            messages.success(request, "Account created! Await admin approval.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


# User Login (Only Approved Users)
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    messages.success(request, "Successfully logged in!")
                    return redirect('home')
                else:
                    messages.error(request, "Your account is pending approval. Access denied.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


# User Logout
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')


# Account Activation
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Your account has been activated. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid activation link.")
    except Exception:
        messages.error(request, "Activation failed.")
    return redirect('home')


# Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('login')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'


# Various Page Views
def about(request):
    return render(request, "about.html", {"about": Aboutpage.objects.all(), "footer": Footer.objects.all()})


def artists(request):
    return render(request, "artists.html", {"artists": Artists.objects.all(), "footer": Footer.objects.all()})


def home(request):
    return render(request, 'home.html', {
        "home": Homepage.objects.all(),
        "about": Aboutpage.objects.all(),
        "footer": Footer.objects.all()
    })


def artworks(request):
    return render(request, "artworks.html", {"artworks": Artworks.objects.all(), "footer": Footer.objects.all()})


def exhibitions(request):
    exhibitions = Exhibition.objects.all()
    for exhibition in exhibitions:
        exhibition.bookings_count = Booking.objects.filter(exhibition=exhibition).count()
        exhibition.available_spots = exhibition.max_capacity - exhibition.bookings_count
        exhibition.is_full = exhibition.bookings_count >= exhibition.max_capacity
    return render(request, "exhibitions.html", {
        "exhibitions": exhibitions,
        "footer": Footer.objects.all()
    })


def contact(request):
    return render(request, "contact.html", {"contact": Contact.objects.all(), "footer": Footer.objects.all()})


# Exhibition Booking System
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from datetime import datetime
import json

from .models import Exhibition, Booking


@require_POST
def book_exhibition(request):
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        exhibition_id = data.get('exhibition_id')
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')

        if not all([exhibition_id, name, email, phone]):
            return JsonResponse({'success': False, 'message': 'All fields are required.'}, status=400)

        exhibition = get_object_or_404(Exhibition, id=exhibition_id)

        if Booking.objects.filter(email=email, exhibition=exhibition).exists():
            return JsonResponse({'success': False, 'message': 'You have already booked this exhibition.'}, status=400)

        bookings_count = Booking.objects.filter(exhibition=exhibition).count()
        if bookings_count >= exhibition.max_capacity:
            return JsonResponse({'success': False, 'message': 'This exhibition is fully booked.'}, status=400)

        booking = Booking.objects.create(
            exhibition=exhibition,
            name=name,
            email=email,
            phone=phone,
            booking_date=datetime.now()
        )

        # Beautiful HTML-styled confirmation email
        subject = '🎨 Booking Confirmation - Your Spot is Reserved!'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [booking.email]

        text_content = f'Thank you {booking.name} for booking "{booking.exhibition.title}". We are looking forward to having you there!'

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
          <div style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); padding: 30px;">
            <h2 style="color: #333333;">🎟️ Booking Confirmation</h2>
            <p style="font-size: 16px; color: #555555;">
                Dear <strong>{booking.name}</strong>,
            </p>
            <p style="font-size: 16px; color: #555555;">
                Thank you for booking your spot at <strong>"{booking.exhibition.title}"</strong>.
            </p>
            <p style="font-size: 16px; color: #555555;">
                We are excited to have you at our exhibition. Please bring this confirmation with you.
            </p>
            <hr style="border: none; border-top: 1px solid #ddd;">
            <p style="font-size: 14px; color: #888888;">📅 Booking Date: {booking.booking_date.strftime('%B %d, %Y %I:%M %p')}</p>
            <p style="font-size: 14px; color: #888888;">📍 Exhibition: {booking.exhibition.title}</p>
            <br>
            <p style="font-size: 14px; color: #888888;">If you have any questions, reply to this email. info@usaniimashariki.com </p>
            <p style="font-size: 14px; color: #888888;">Warm regards,<br><strong>Usanii Mashariki Art Gallery</strong></p>
          </div>
        </body>
        </html>
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return JsonResponse({'success': True, 'message': 'Booking successful! A confirmation email has been sent to your email address.'})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid data format.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'}, status=500)


def booking_list(request):
    if not request.user.is_authenticated:
        return redirect('login')

    bookings = Booking.objects.select_related('exhibition').all()
    return render(request, "booking_list.html", {
        "bookings": bookings,
        "footer": Footer.objects.all()
    })


def cancel_booking(request, booking_id):
    if not request.user.is_authenticated:
        return redirect('login')

    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking has been cancelled.')
        return redirect('booking_list')
    return render(request, "confirm_cancel.html", {"booking": booking})


# Send Inquiry Email
def send_inquiry_email(request):
    if request.method == 'POST':
        try:
            send_mail(
                "New Inquiry Received",
                f"Name: {request.POST.get('name', 'Unknown')}\nEmail: {request.POST.get('email', 'No Email Provided')}\nPhone: {request.POST.get('phone', 'N/A')}\nMessage: {request.POST.get('message', 'No Message')}",
                settings.EMAIL_HOST_USER,
                ['fatmahussein355@gmail.com']
            )
            return JsonResponse({'success': True, 'message': 'Inquiry sent successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


def moreartist(request):
    return render(request, "moreartist.html", {
        "moreartist": Moreartist.objects.all(),
        "footer": Footer.objects.all()
    })
