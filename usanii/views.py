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

from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .forms import RegisterForm


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Let the form handle saving and is_active=False

            # Send registration confirmation email
            subject = 'Registration Successful - Awaiting Approval'
            message = render_to_string('registration_confirmation_email.html', {
                'user': user,
            })
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=message
            )

            messages.success(
                request,
                "Your account has been created successfully! Please wait for admin approval. "
                "A confirmation email has been sent to your email address."
            )
            return redirect('registration_success')
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

def registration_success(request):
    return render(request, 'registration_success.html')

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
       # "about": Aboutpage.objects.all(),
        "footer": Footer.objects.all()
    })


def artworks(request):
    return render(request, "artworks.html", {"artworks": Artworks.objects.all(), "footer": Footer.objects.all()})


# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Artworks, Cart, CartItem
from django.http import JsonResponse


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
        if created and not request.session.session_key:
            request.session.create()
            cart.session_key = request.session.session_key
            cart.save()
    return cart


# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cart, CartItem, Artworks

from django.http import JsonResponse


def add_to_cart(request, artwork_id):
    artwork = get_object_or_404(Artworks, id=artwork_id)

    # Get or create cart
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
        if created and not request.session.session_key:
            request.session.create()
            cart.session_key = request.session.session_key
            cart.save()

    # Get existing cart item or create new one
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        artwork=artwork,
        defaults={'quantity': 1}  # Only set quantity=1 when creating new
    )

    if not created:
        # If item already exists, increment quantity
        cart_item.quantity += 1
        cart_item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Successfully added {artwork.title} to your cart',
            'cart_count': cart.items.count(),
            'new_quantity': cart_item.quantity,
            'item_total': cart_item.total_price,
            'cart_total': cart.total_price
        })

    return redirect('artworks')

def view_cart(request):
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
        else:
            cart = Cart.objects.get(session_key=request.session.session_key)
    except Cart.DoesNotExist:
        cart = None

    return render(request, "cart.html", {
        "cart": cart,
        "footer": Footer.objects.all()
    })

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = cart_item.cart

    # Check if the cart belongs to the user or session
    if (request.user.is_authenticated and cart.user == request.user) or \
            (not request.user.is_authenticated and cart.session_key == request.session.session_key):
        cart_item.delete()
        messages.success(request, 'Artwork removed from cart successfully!')
    else:
        messages.error(request, 'You cannot remove this item.')

    return redirect('view_cart')


def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = cart_item.cart

    if (request.user.is_authenticated and cart.user == request.user) or \
            (not request.user.is_authenticated and cart.session_key == request.session.session_key):
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully!')
        else:
            cart_item.delete()
            messages.success(request, 'Artwork removed from cart successfully!')
    else:
        messages.error(request, 'You cannot update this item.')

    return redirect('view_cart')


def checkout(request):
    return render(request, "checkout.html", {
        "footer": Footer.objects.all()
    })

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


from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
import re
from .models import Contact, Footer  # Make sure to import your models


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Validation
        if not re.match(r'^[A-Za-z\s]+$', name):
            messages.error(request, 'Name should contain only letters and spaces')
            return redirect('contact')

        if not re.match(r'^[A-Za-z\s]+$', subject):
            messages.error(request, 'Subject should contain only letters and spaces')
            return redirect('contact')

        if not email or '@' not in email:
            messages.error(request, 'Please enter a valid email address')
            return redirect('contact')

        # Send email
        try:
            send_mail(
                f"{subject} - From {name}",
                f"Message from: {name} <{email}>\n\n{message}",
                settings.DEFAULT_FROM_EMAIL,
                ['fatmahussein355@gmail.com'],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
        except Exception as e:
            messages.error(request, f'There was an error sending your message: {str(e)}')

        return redirect('contact')

    # For GET requests
    return render(request, "contact.html", {
        "contact": Contact.objects.all(),
        "footer": Footer.objects.all()
    })


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


from datetime import datetime
from django.db.models import Count, Q, Case, When, F, ExpressionWrapper, FloatField
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_http_methods
from .models import Artists, Artworks, Exhibition, Booking, Footer

@user_passes_test(lambda u: u.is_superuser)
def generate_reports(request):
    # Date range handling
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Convert dates if provided
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Base querysets
    artists = Artists.objects.all()
    artworks = Artworks.objects.all()
    exhibitions = Exhibition.objects.all()
    bookings = Booking.objects.all()

    # Apply date filters if provided
    if start_date and end_date:
        exhibitions = exhibitions.filter(
            Q(date__range=[start_date, end_date]) |
            Q(created_at__date__range=[start_date, end_date])
        )
        bookings = bookings.filter(booking_date__date__range=[start_date, end_date])

    # Generate report data
    report_data = {
        'total_artists': artists.count(),
        'total_artworks': artworks.count(),
        'recent_exhibitions': exhibitions.count(),
        'total_bookings': bookings.count(),
        'cancelled_bookings': bookings.filter(is_confirmed=False).count(),
        'confirmed_bookings': bookings.filter(is_confirmed=True).count(),
        'start_date': start_date.strftime('%Y-%m-%d') if start_date else '',
        'end_date': end_date.strftime('%Y-%m-%d') if end_date else '',
    }

    # For AJAX requests, return JSON for charts
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        chart_data = {
            'artists_by_artwork': get_artists_by_artwork_data(),
            'bookings_trend': get_bookings_trend_data(start_date, end_date),
            'exhibition_attendance': get_exhibition_attendance_data(),
        }
        return JsonResponse({'report_data': report_data, 'chart_data': chart_data})

    return render(request, 'reports/report.html', {
        'report_data': report_data,
        'footer': Footer.objects.all()
    })

def get_artists_by_artwork_data():
    try:
        artists = Artists.objects.annotate(
            num_artworks=Count('artworks')  # Changed from artwork_count to num_artworks
        ).filter(
            num_artworks__gt=0
        ).order_by('-num_artworks')

        return {
            'labels': [artist.name for artist in artists],
            'data': [artist.num_artworks for artist in artists],  # Updated field name
        }
    except Exception as e:
        print(f"Error in get_artists_by_artwork_data: {str(e)}")
        return {
            'labels': [],
            'data': [],
        }

def get_bookings_trend_data(start_date=None, end_date=None):
    from django.db.models.functions import TruncDay

    bookings = Booking.objects.all()
    if start_date and end_date:
        bookings = bookings.filter(booking_date__date__range=[start_date, end_date])

    daily_bookings = bookings.annotate(day=TruncDay('booking_date')) \
        .values('day') \
        .annotate(count=Count('id')) \
        .order_by('day')

    return {
        'labels': [entry['day'].strftime('%Y-%m-%d') for entry in daily_bookings],
        'data': [entry['count'] for entry in daily_bookings],
    }

def get_exhibition_attendance_data():
    exhibitions = Exhibition.objects.annotate(
        bookings_count=Count('bookings'),
        attendance_percentage=Case(
            When(max_capacity=0, then=0),
            default=ExpressionWrapper(
                F('current_attendees') * 100.0 / F('max_capacity'),
                output_field=FloatField()
            ),
            output_field=FloatField()
        )
    ).order_by('-attendance_percentage')

    return {
        'labels': [exh.title for exh in exhibitions],
        'data': [float(exh.attendance_percentage) for exh in exhibitions],
        'max_capacity': [exh.max_capacity for exh in exhibitions],
        'current_attendees': [exh.current_attendees for exh in exhibitions],
        'bookings_count': [exh.bookings_count for exh in exhibitions],
    }


# views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Cart, Footer, Order, Payment
from .mpesa import initiate_stk_push
import uuid
import json
from django.utils import timezone


def checkout(request):
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
        else:
            cart = Cart.objects.get(session_key=request.session.session_key)
    except Cart.DoesNotExist:
        return redirect('view_cart')

    return render(request, "checkout.html", {
        "cart": cart,
        "footer": Footer.objects.all()
    })


def process_payment(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')
        reference = f"ART{str(uuid.uuid4().int)[:8]}"

        # Format phone number
        if phone.startswith('0'):
            phone = f"254{phone[1:]}"
        elif phone.startswith('+'):
            phone = phone[1:]

        # Create simulated payment
        payment = Payment.objects.create(
            phone_number=phone,
            amount=amount,
            receipt_number=f"SIM{timezone.now().strftime('%Y%m%d%H%M%S')}",
            status='completed',
            reference=reference
        )

        # Create order
        order = Order.objects.create(
            order_number=reference,
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key if not request.user.is_authenticated else None,
            total_amount=amount,
            payment=payment
        )

        return JsonResponse({
            'success': True,
            'message': '[SIMULATION] Payment successful! No real STK Push was sent.',
            'reference': reference
        })

    return redirect('checkout')


def payment_processing(request):
    reference = request.GET.get('reference')
    return render(request, "payment_processing.html", {
        'reference': reference,
        'footer': Footer.objects.all()
    })


# views.py
def payment_success(request):
    reference = request.GET.get('reference')
    try:
        order = Order.objects.get(order_number=reference)

        if request.method == 'POST':
            # Handle delivery information form submission
            order.payment.delivery_address = request.POST.get('delivery_address')
            order.payment.customer_email = request.POST.get('customer_email')
            order.payment.save()
            messages.success(request, "Delivery information saved successfully!")
            # Redirect back to the same page with the reference
            return redirect(f'/payment-success/?reference={reference}')

        # Clear cart after successful payment
        if request.user.is_authenticated:
            Cart.objects.filter(user=request.user).delete()
        else:
            Cart.objects.filter(session_key=request.session.session_key).delete()
            if 'cart_id' in request.session:
                del request.session['cart_id']

        return render(request, "payment_success.html", {
            'order': order,
            'payment': order.payment,
            'footer': Footer.objects.all()
        })
    except Order.DoesNotExist:
        messages.error(request, "Order not found")
        return redirect('home')


# These can be kept but won't be used in simulation
@csrf_exempt
def payment_callback(request):
    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})


@csrf_exempt
def pay_with_mpesa(request):
    return JsonResponse({"message": "Simulation mode - no real payments"})


@csrf_exempt
def mpesa_callback(request):
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})