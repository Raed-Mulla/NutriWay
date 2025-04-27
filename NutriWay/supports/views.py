from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from .models import ContactUs
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def contact_us_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message_text = request.POST.get('message')


        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.", "alert-danger")
            return redirect('supports:contact_us')
        ContactUs.objects.create(
            name=name,
            email=email,
            message=message_text,
        )
        
        messages.success(request, "Your message has been sent successfully. Thank you for contacting us!", "alert-success")

        send_mail(
            subject='NutriHeaven - Contact Us Confirmation',
            message=(
                f"Hi {name},\n\n"
                "We have received your message and our support team will get back to you shortly.\n\n"
                "Thank you for contacting NutriHeaven!\n\n"
                "Best regards,\n"
                "NutriHeaven Support Team"
            ),

            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        return redirect('supports:contact_us')
    return render(request, 'supports/contact_us.html')


