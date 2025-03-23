from django.shortcuts import render, redirect
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


from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


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
    except Exception as e:
        messages.error(request, "Activation failed.")

    return redirect('home')
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView
from django.urls import reverse_lazy

class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('login')
from django.contrib.auth.views import PasswordResetCompleteView

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'


# Views for Various Pages
def about(request):
    about = Aboutpage.objects.all()
    footer = Footer.objects.all()
    return render(request, "about.html", {"about": about, "footer": footer})

def artists(request):
    artists = Artists.objects.all()
    footer = Footer.objects.all()
    return render(request, "artists.html", {"artists": artists, "footer": footer})

def home(request):
    home = Homepage.objects.all()
    about = Aboutpage.objects.all()
    footer = Footer.objects.all()
    context = {"home": home, "about": about, "footer": footer}
    return render(request, 'home.html', context)

def artworks(request):
    artworks = Artworks.objects.all()
    footer = Footer.objects.all()
    return render(request, "artworks.html", {"artworks": artworks, "footer": footer})

def exhibitions(request):
    exhibitions = Exhibitions.objects.all()
    footer = Footer.objects.all()
    return render(request, "exhibitions.html", {"exhibitions": exhibitions, "footer": footer})

def contact(request):
    contact = Contact.objects.all()
    footer = Footer.objects.all()
    return render(request, "contact.html", {"contact": contact, "footer": footer})

def reservation(request):
    footer = Footer.objects.all()
    return render(request, "reservation.html", {"footer": footer})

def booked(request):
    customers = Customer.objects.all()
    footer = Footer.objects.all()
    return render(request, "booked.html", {"data": customers, "footer": footer})

def delete(request, id):
    customer = Customer.objects.get(id=id)
    customer.delete()
    footer = Footer.objects.all()
    return redirect('booked')

def insertdata(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        event = request.POST.get('event', 'Opening Event')

        Customer.objects.create(name=name, email=email, phone=phone, date=date, time=time, event=event)
        return redirect("booked")

    return redirect("booked")

def edit(request, id):
    customer = Customer.objects.get(id=id)
    if request.method == 'POST':
        customer.name = request.POST.get('name')
        customer.email = request.POST.get('email')
        customer.phone = request.POST.get('phone')
        customer.date = request.POST.get('date')
        customer.time = request.POST.get('time')
        customer.event = request.POST.get('event')
        customer.save()
        return redirect("booked")

    return render(request, 'edit.html', {'Customer': customer})

def send_inquiry_email(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name', 'Unknown')
            email = request.POST.get('email', 'No Email Provided')
            phone = request.POST.get('phone', 'N/A')
            message = request.POST.get('message', 'No Message')

            subject = "New Inquiry Received"
            body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"

            send_mail(subject, body, settings.EMAIL_HOST_USER, ['fatmahussein355@gmail.com'])

            return JsonResponse({'success': True, 'message': 'Inquiry sent successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

def moreartist(request):
    moreartist = Moreartist.objects.all()
    footer = Footer.objects.all()
    return render(request, "moreartist.html", {"moreartist": moreartist, "footer": footer})