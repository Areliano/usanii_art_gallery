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


from datetime import datetime, timedelta
from django.db.models import Count, Q, Case, When, F, ExpressionWrapper, FloatField, Sum, Avg
from django.db.models.functions import TruncMonth, TruncDay
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User # Required for customer reports

# Import all your relevant models
from .models import Artists, Artworks, Exhibition, Booking, Footer, Order, Payment, OrderItem, Cart

@user_passes_test(lambda u: u.is_superuser)
def generate_reports(request):
    # Date range handling
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_date = None
    end_date = None

    # Parse dates if provided
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # Set default date range if not provided (e.g., last 30 days)
    if not start_date and not end_date:
        end_date = timezone.localdate()
        start_date = end_date - timedelta(days=30)
    elif not start_date and end_date: # If only end date is provided
        start_date = end_date - timedelta(days=30)
    elif start_date and not end_date: # If only start date is provided
        end_date = timezone.localdate() # Set end date to today

    # Base querysets
    artists_qs = Artists.objects.all()
    artworks_qs = Artworks.objects.all()
    exhibitions_qs = Exhibition.objects.all()
    bookings_qs = Booking.objects.all()
    payments_qs = Payment.objects.all()
    orders_qs = Order.objects.all()
    order_items_qs = OrderItem.objects.all()

    # Apply date filters to relevant querysets
    if start_date and end_date:
        exhibitions_qs = exhibitions_qs.filter(
            Q(date__range=[start_date, end_date]) |
            Q(created_at__date__range=[start_date, end_date])
        ).distinct()

        bookings_qs = bookings_qs.filter(booking_date__date__range=[start_date, end_date])
        payments_qs = payments_qs.filter(transaction_date__date__range=[start_date, end_date])
        orders_qs = orders_qs.filter(created_at__date__range=[start_date, end_date])
        order_items_qs = order_items_qs.filter(order__created_at__date__range=[start_date, end_date])

    # --- Generate Report Data (Summary Cards) ---
    total_revenue = payments_qs.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    total_orders = orders_qs.filter(payment__status='completed').count()
    average_order_value_agg = orders_qs.filter(payment__status='completed').aggregate(Avg('total_amount'))['total_amount__avg']
    average_order_value = round(float(average_order_value_agg), 2) if average_order_value_agg else 0

    # Ensure all numeric values are properly converted to float
    report_data = {
        'total_artists': artists_qs.count(),
        'total_artworks': artworks_qs.count(),
        'active_exhibitions': exhibitions_qs.filter(date__gte=timezone.localdate()).count(),
        'total_revenue_collected': float(total_revenue),
        'total_orders_placed': total_orders,
        'successful_payments': payments_qs.filter(status='completed').count(),
        'total_bookings': bookings_qs.count(),
        'confirmed_bookings': bookings_qs.filter(is_confirmed=True).count(),
        'cancelled_bookings': bookings_qs.filter(is_confirmed=False).count(),
        'average_order_value': average_order_value,
        'start_date': start_date.strftime('%Y-%m-%d') if start_date else '',
        'end_date': end_date.strftime('%Y-%m-%d') if end_date else '',
    }

    # For AJAX requests, return JSON for charts and tables
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        chart_data = {
            'artists_by_artwork': get_artists_by_artwork_data(),
            'bookings_trend': get_bookings_trend_data(start_date, end_date),
            'exhibition_attendance': get_exhibition_attendance_data(),
            'monthly_revenue_trend': get_monthly_revenue_trend(start_date, end_date),
            'top_selling_artworks': get_top_selling_artworks_data(start_date, end_date),
            'artwork_category_distribution': get_artwork_category_distribution(),
            'artist_revenue_contribution': get_artist_revenue_contribution_data(start_date, end_date),
            'most_frequent_customers': get_most_frequent_customers_data(start_date, end_date),
        }
        return JsonResponse({'report_data': report_data, 'chart_data': chart_data})

    return render(request, 'reports/report.html', {
        'report_data': report_data,
        'footer': Footer.objects.all()
    })

# --- Helper functions for charts and detailed data ---
from django.db.models import Count
from .models import Artists

def get_artists_by_artwork_data():
    """Returns data for artists by the number of artworks they have."""
    try:
        artists = Artists.objects.annotate(
            num_artworks=Count('artworks')  # 'artworks' is correct based on your related_name
        ).filter(
            num_artworks__gt=0
        ).order_by('-num_artworks')[:10]  # Top 10 artists by artwork count

        return {
            'labels': [artist.name for artist in artists],
            'data': [artist.num_artworks for artist in artists],
        }
    except Exception as e:
        print(f"Error in get_artists_by_artwork_data: {e}")
        return {'labels': [], 'data': []}

def get_artist_revenue_contribution_data(start_date=None, end_date=None):
    """Returns total revenue generated by each artist's artworks."""
    # Create a base filter for the date range if provided
    date_filter = Q()
    if start_date and end_date:
        date_filter = Q(artworks__orderitem__order__created_at__date__range=[start_date, end_date])

    artist_revenue = Artists.objects.annotate(
        total_revenue_from_sales=Coalesce(
            Sum(
                F('artworks__orderitem__quantity') * F('artworks__orderitem__price_at_purchase'),
                filter=Q(artworks__orderitem__order__payment__status='completed') & date_filter,
                output_field=FloatField()
            ),
            0.0
        )
    ).filter(total_revenue_from_sales__gt=0).order_by('-total_revenue_from_sales')[:10]

    return {
        'labels': [artist.name for artist in artist_revenue],
        'data': [float(artist.total_revenue_from_sales) for artist in artist_revenue],
    }

def get_bookings_trend_data(start_date=None, end_date=None):
    """Returns daily booking counts within a date range."""
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
    """Returns attendance data for exhibitions (current attendees vs. max capacity)."""
    exhibitions = Exhibition.objects.annotate(
        attendance_percentage=Case(
            When(max_capacity=0, then=0), # Avoid division by zero
            default=ExpressionWrapper(
                F('current_attendees') * 100.0 / F('max_capacity'),
                output_field=FloatField()
            ),
            output_field=FloatField()
        )
    ).order_by('-attendance_percentage')[:10] # Top 10 by attendance percentage

    return {
        'labels': [exh.title for exh in exhibitions],
        'data': [round(float(exh.attendance_percentage), 2) for exh in exhibitions],
        'max_capacity': [exh.max_capacity for exh in exhibitions],
        'current_attendees': [exh.current_attendees for exh in exhibitions],
    }

# NEW: Monthly Revenue Trend
def get_monthly_revenue_trend(start_date=None, end_date=None):
    """Returns total completed revenue aggregated by month."""
    payments = Payment.objects.filter(status='completed')
    if start_date and end_date:
        payments = payments.filter(transaction_date__date__range=[start_date, end_date])

    monthly_revenue = payments.annotate(month=TruncMonth('transaction_date')) \
        .values('month') \
        .annotate(total_amount=Sum('amount')) \
        .order_by('month')

    return {
        'labels': [entry['month'].strftime('%Y-%m') for entry in monthly_revenue],
        'data': [float(entry['total_amount']) for entry in monthly_revenue],
    }

# NEW: Top Selling Artworks
def get_top_selling_artworks_data(start_date=None, end_date=None):
    """Returns data for top 5 selling artworks by revenue and quantity."""
    order_items = OrderItem.objects.select_related('artwork', 'order__payment').filter(order__payment__status='completed')
    if start_date and end_date:
        order_items = order_items.filter(order__created_at__date__range=[start_date, end_date])

    top_artworks = order_items.values('artwork__title', 'artwork__id') \
        .annotate(total_quantity_sold=Sum('quantity'), total_revenue=Sum(F('quantity') * F('price_at_purchase'))) \
        .order_by('-total_revenue')[:5] # Top 5 selling artworks by revenue

    return {
        'labels': [item['artwork__title'] for item in top_artworks],
        'quantity_data': [item['total_quantity_sold'] for item in top_artworks],
        'revenue_data': [float(item['total_revenue']) for item in top_artworks],
        'details': [ # Useful for rendering as a table
            {'title': item['artwork__title'], 'quantity': item['total_quantity_sold'], 'revenue': round(float(item['total_revenue']), 2)}
            for item in top_artworks
        ]
    }

# NEW: Artwork Category Distribution
def get_artwork_category_distribution():
    """Returns the count of artworks per category."""
    # This assumes Artworks has a 'category' field. Adjust 'category' to your field name (e.g., 'medium') if different.
    artwork_categories = Artworks.objects.values('category').annotate(count=Count('id')).order_by('-count')

    return {
        'labels': [entry['category'] if entry['category'] else 'Uncategorized' for entry in artwork_categories],
        'data': [entry['count'] for entry in artwork_categories],
    }

# NEW: Artist Revenue Contribution
def get_artist_revenue_contribution_data(start_date=None, end_date=None):
    """Returns total revenue generated by each artist's artworks."""
    artist_revenue = Artists.objects.annotate(
        total_revenue_from_sales=Sum(
            Case(
                When(artworks__orderitem__order__payment__status='completed', then=F('artworks__orderitem__quantity') * F('artworks__orderitem__price_at_purchase')),
                default=0,
                output_field=FloatField()
            ),
            # Filter for completed sales within the date range
            filter=Q(
                artworks__orderitem__order__payment__status='completed',
                artworks__orderitem__order__created_at__date__range=[start_date, end_date] if start_date and end_date else Q()
            )
        )
    ).order_by('-total_revenue_from_sales')[:10] # Top 10 artists by revenue

    # Filter out artists with no sales or only 0 sales
    filtered_artists = [
        artist for artist in artist_revenue
        if artist.total_revenue_from_sales is not None and artist.total_revenue_from_sales > 0
    ]

    return {
        'labels': [artist.name for artist in filtered_artists],
        'data': [round(float(artist.total_revenue_from_sales), 2) for artist in filtered_artists],
    }

# NEW: Most Frequent Customers (by Orders & Bookings)
def get_most_frequent_customers_data(start_date=None, end_date=None):
    """Returns a list of most frequent customers based on orders and bookings."""
    customer_data = {}

    # Aggregate orders by user
    orders_by_user = Order.objects.filter(payment__status='completed')
    if start_date and end_date:
        orders_by_user = orders_by_user.filter(created_at__date__range=[start_date, end_date])

    for order in orders_by_user.select_related('user'):
        user_id = order.user.id if order.user else f"guest_{order.session_key or 'anon'}"
        username = order.user.username if order.user else f"Guest ({order.session_key[:5] if order.session_key else 'N/A'})"
        if user_id not in customer_data:
            customer_data[user_id] = {'customer_name': username, 'orders': 0, 'bookings': 0, 'total_spend': 0.0}
        customer_data[user_id]['orders'] += 1
        customer_data[user_id]['total_spend'] += float(order.total_amount)

    # Aggregate bookings by user (assuming Booking model has a 'user' ForeignKey)
    bookings_by_user = Booking.objects.all()
    if start_date and end_date:
        bookings_by_user = bookings_by_user.filter(booking_date__date__range=[start_date, end_date])

    for booking in bookings_by_user.select_related('user'):
        if booking.user: # Only count if linked to a registered user
            user_id = booking.user.id
            username = booking.user.username
            if user_id not in customer_data:
                customer_data[user_id] = {'customer_name': username, 'orders': 0, 'bookings': 0, 'total_spend': 0.0}
            customer_data[user_id]['bookings'] += 1

    # Convert to a list of dictionaries and sort
    sorted_customers = sorted(
        [v for k, v in customer_data.items()],
        key=lambda x: (x['orders'] + x['bookings'], x['total_spend']), # Sort by total activity, then spend
        reverse=True
    )[:10] # Top 10 most frequent customers

    return sorted_customers


# Assuming this is your app's main views.py file
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
# Ensure all necessary models are imported:
from .models import Cart, Footer, Order, Payment, Artworks, CartItem, OrderItem # Added OrderItem

import uuid
import json
from django.utils import timezone


def checkout(request):
    try:
        # Use .first() to handle cases where there might be multiple carts (though ideally there should be one)
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            cart = Cart.objects.filter(session_key=request.session.session_key).first()

        if not cart or not cart.items.exists(): # Check if cart exists AND has items
            messages.info(request, "Your cart is empty. Add some artworks before checking out!")
            return redirect('artworks') # Redirect to artworks page if cart is empty
    except Cart.DoesNotExist:
        messages.error(request, "Your cart does not exist.")
        return redirect('artworks') # Redirect to artworks page if cart not found

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

        # Get the cart for the current user/session
        current_cart = None
        if request.user.is_authenticated:
            current_cart = Cart.objects.filter(user=request.user).first()
        else:
            current_cart = Cart.objects.filter(session_key=request.session.session_key).first()

        if not current_cart or not current_cart.items.exists():
            return JsonResponse({
                'success': False,
                'message': 'Your cart is empty. Cannot process payment.',
                'reference': None
            })

        # --- SIMULATED PAYMENT SUCCESS ---
        # In a real system, you'd initiate the STK push here and wait for confirmation.
        # For this project, we directly mark as completed.
        payment = Payment.objects.create(
            phone_number=phone,
            amount=amount,
            receipt_number=f"SIM{timezone.now().strftime('%Y%m%d%H%M%S')}",
            status='completed', # Directly mark as completed for simulation
            reference=reference
        )

        # Create the Order
        order = Order.objects.create(
            order_number=reference,
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key if not request.user.is_authenticated else None,
            total_amount=current_cart.total_price, # Use cart's total price
            payment=payment
        )

        # Transfer CartItems to OrderItems and clear the cart
        for cart_item in current_cart.items.all():
            OrderItem.objects.create(
                order=order,
                artwork=cart_item.artwork,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.artwork.price # Record the price at the time of purchase
            )
        current_cart.items.all().delete() # Delete all CartItems
        current_cart.delete() # Delete the Cart itself

        messages.success(request, "[SIMULATION] Payment successful and order placed! No real STK Push was sent.")
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


def payment_success(request):
    reference = request.GET.get('reference')
    try:
        order = Order.objects.get(order_number=reference)

        if request.method == 'POST':
            # Handle delivery information form submission
            if order.payment: # Ensure payment object exists
                order.payment.delivery_address = request.POST.get('delivery_address')
                order.payment.customer_email = request.POST.get('customer_email')
                order.payment.save()
                messages.success(request, "Delivery information saved successfully!")
                return redirect(f'/payment-success/?reference={reference}')
            else:
                messages.error(request, "Payment details not found for this order.")


        return render(request, "payment_success.html", {
            'order': order,
            'payment': order.payment,
            'footer': Footer.objects.all()
        })
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('home')

# Keep your existing artworks, add_to_cart, view_cart, remove_from_cart, update_cart_item functions as is.
# Ensure they correctly import Artworks, Cart, CartItem, Footer.

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