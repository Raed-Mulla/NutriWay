from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from .models import ContactUs
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods

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
            subject='NutriWay - Contact Us Confirmation',
            message=(
                f"Hi {name},\n\n"
                "We have received your message and our support team will get back to you shortly.\n\n"
                "Thank you for contacting NutriWay!\n\n"
                "Best regards,\n"
                "NutriWay Support Team"
            ),

            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        return redirect('supports:contact_us')
    return render(request, 'supports/contact_us.html')



def contact_messages(request : HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to access this page.", "alert-danger")
        return redirect('accounts:login_view')

    messages_list = ContactUs.objects.all().order_by('-created_at')
    
    return render(request, 'supports/contact_messages.html', {'messages_list': messages_list})




@login_required
@require_http_methods(["GET", "POST"])
def reply_message(request : HttpRequest, message_id : int) -> HttpResponse:
    if not request.user.is_staff:
        return redirect('core:home_view')
    

    message_obj = ContactUs.objects.get(id=message_id)

    if request.method == 'POST':
        reply_text = request.POST.get('reply_message')

        if reply_text:
            # Send custom email to the customer
            send_mail(
                subject='NutriWay - Reply to Your Support Request',
                message=(
                    f"Hi {message_obj.name},\n\n"
                    f"{reply_text}\n\n"
                    "Thank you for contacting NutriWay!\n"
                    "Best regards,\n"
                    "NutriWay Support Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[message_obj.email],
                fail_silently=False,
            )

            # Mark as Resolved
            message_obj.status = 'Resolved'
            message_obj.save()

            messages.success(request, "Reply sent successfully and marked as resolved." , "alert-success")
            return redirect('supports:contact_messages')

    return render(request, 'supports/reply_message.html', {
        'message_obj': message_obj
    })
