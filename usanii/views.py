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
from .models import Aboutpage, Artists, Homepage, Artworks, Exhibitions, Contact, Footer, Customer, Moreartist
from django.http import JsonResponse
from datetime import datetime
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

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
    return render(request, 'home.html', {"home": Homepage.objects.all(), "about": Aboutpage.objects.all(), "footer": Footer.objects.all()})

def artworks(request):
    return render(request, "artworks.html", {"artworks": Artworks.objects.all(), "footer": Footer.objects.all()})

def exhibitions(request):
    return render(request, "exhibitions.html", {"exhibitions": Exhibitions.objects.all(), "footer": Footer.objects.all()})

def contact(request):
    return render(request, "contact.html", {"contact": Contact.objects.all(), "footer": Footer.objects.all()})

def reservation(request):
    return render(request, "reservation.html", {"footer": Footer.objects.all()})

# Updated Booked View
def booked(request):
    customers = Customer.objects.filter(is_approved=True)  # Show only approved customers
    return render(request, "booked.html", {"data": customers, "footer": Footer.objects.all()})

# Delete Customer
def delete(request, id):
    get_object_or_404(Customer, id=id).delete()
    return redirect('booked')

# Insert Customer Data
def insertdata(request):
    if request.method == 'POST':
        Customer.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            date=request.POST.get('date'),
            time=request.POST.get('time'),
            event=request.POST.get('event', 'Opening Event')
        )
    return redirect("booked")

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime
from .models import Customer  # Ensure Customer model is imported

from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Customer

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import Customer
from datetime import datetime

def edit(request, id):
    # Check if the customer exists before using get_object_or_404
    if not Customer.objects.filter(id=id).exists():
        return HttpResponse(f"Customer with ID {id} does not exist", status=404)

    customer = get_object_or_404(Customer, id=id)

    if request.method == 'POST':
        customer.name = request.POST.get('name', customer.name)
        customer.email = request.POST.get('email', customer.email)
        customer.phone = request.POST.get('phone', customer.phone)

        # ✅ Ensure correct key for date input
        date_str = request.POST.get('datetime')
        if date_str:
            try:
                customer.date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
                return redirect("edit", id=id)
        else:
            customer.date = None  # ✅ Allow blank date

        customer.time = request.POST.get('time', customer.time)
        customer.event = request.POST.get('event_name', customer.event)
        customer.is_approved = False  # Ensure re-approval

        try:
            print(f"Saving: Name={customer.name}, Date={customer.date}, Time={customer.time}")
            customer.save()
            messages.success(request, "Successfully updated your details. Wait for admin approval.")
            return redirect("edit", id=id)  # ✅ Redirect back to `edit.html` so message is displayed
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect("edit", id=id)

    return render(request, 'edit.html', {'customer': customer})

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

# Approve and Disapprove Customers
def approve_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.is_approved = True
    customer.save()
    messages.success(request, f"{customer.name} has been approved.")
    return redirect('booked')

def disapprove_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.is_approved = False
    customer.save()
    messages.error(request, f"{customer.name} has been disapproved.")
    return redirect('booked')

def moreartist(request):
    moreartist = Moreartist.objects.all()
    footer = Footer.objects.all()
    return render(request, "moreartist.html", {"moreartist": moreartist, "footer": footer})
