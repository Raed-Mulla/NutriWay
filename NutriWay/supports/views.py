from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from .models import ContactUs


def contact_us_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        ContactUs.objects.create(
            name=name,
            email=email,
            message=message,
            status='new'
        )
    return render(request, 'supports/contact_us.html')

# Why ?
def contact_thanks_view(request : HttpRequest) -> HttpResponse:
    return render(request, 'supports/thanks.html')

