# Create your views here.

from django.shortcuts import render, redirect

from .models import Aboutpage, Artists, Homepage, Artworks, Exhibitions, Contact, Footer, Customer

from django.utils import timezone

from django.http import HttpResponse
from django.core.mail import send_mail
from django.http import JsonResponse

def about(request):
    about = Aboutpage.objects.all
    footer = Footer.objects.all()
    return render(request, "about.html", {"about": about, "footer": footer})

def artists(request):
    artists = Artists.objects.all()
    footer = Footer.objects.all()
    return render(request, "artists.html", {"artists": artists, "footer":footer})


def home(request):
    home = Homepage.objects.all()
    about = Aboutpage.objects.all
    footer = Footer.objects.all()
    context = {"home": home, "about": about, "footer": footer}
    return render(request, 'home.html', context)

def artworks(request):
    artworks = Artworks.objects.all()
    footer = Footer.objects.all()
    return render(request, "menu.html", {"arwtorks": artworks, "footer": footer})

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
    return render(request, "reservation.html", {"link": "reservation", "footer":footer })


def booked(request):
    customers = Customer.objects.all()
    footer = Footer.objects.all()
    return render(request, "booked.html", {"link": "booked", "data": customers, "footer":footer})



def delete(request, id):
    satisfied_customer = Customer.objects.get(id=id)
    satisfied_customer.delete()
    footer = Footer.objects.all()

    return render(request, 'booked.html', {"footer":footer})

def footer(request):
    footer = Footer.objects.all()
    return render(request, 'common.html', {"footer":footer})

def insertdata(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        person = request.POST.get('person')

        Customer1 = Customer(name=name, email=email, phone=phone, date=date, time=time, person=person)
        Customer1.save()
        return redirect("/booked")

    return redirect("/booked")


def edit(request, id):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        person = request.POST.get('person')

        satisfied_customer = Customer.objects.get(id=id)

        satisfied_customer.name = name
        satisfied_customer.email = email
        satisfied_customer.phone = phone
        satisfied_customer.datetime = date
        satisfied_customer.time = time
        satisfied_customer.person = person

        satisfied_customer.save()
    satisfied_customer = Customer.objects.get(id=id)


    return render(request, 'edit.html', {'Customer': satisfied_customer})
    return redirect("/booked")

import logging
from django.core.mail import send_mail
from django.http import JsonResponse

logger = logging.getLogger(__name__)  # Enable logging

from django.core.mail import EmailMessage
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def send_inquiry_email(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name', 'Unknown')
            email = request.POST.get('email', 'No Email Provided')  # Customer's email
            phone = request.POST.get('phone', 'N/A')
            message = request.POST.get('message', 'No Message')

            subject = "New Inquiry Received"
            body = f"""
            Name: {name}
            Email: {email}
            Phone: {phone}
            Message: {message}
            """

            email_message = EmailMessage(
                subject=subject,
                body=body,
                from_email='fatmawanjiku566@gmail.com',  # Must be your verified email
                to=['fatmahussein355@gmail.com'],  # Receiver email
                reply_to=[email]  # Customer's email as reply-to
            )

            send_status = email_message.send(fail_silently=False)

            if send_status:
                logger.info(f"Inquiry email sent from {email}.")
                return JsonResponse({'success': True, 'message': 'Inquiry sent successfully!'})


            logger.error("Email failed to send.")
            return JsonResponse({'success': False, 'message': 'Failed to send email.'}, status=500)

        except Exception as e:
            logger.error(f"Email error: {str(e)}")
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

def moreartist(request):
    artists = Artists.objects.all()
    return render(request, "moreartist.html", {"artists":artists})


