from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from .models import SpecialistRequest
from .forms import SpecialistRequestForm
from accounts.models import Specialist, Certificate , Director
from specialists.models import SubscriptionPlan
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

def specialist_request (request:HttpRequest):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in.", "alert-danger")
        return redirect('accounts:login_view')

    if not Director.objects.filter(user=request.user).exists():
        messages.error(request, "You are not authorized to access this page.", "alert-danger")
        return redirect('core:home_view')

    requests = SpecialistRequest.objects.filter(status="pending")
    return render(request , 'directors/specialist_request.html' , {"requests" : requests})


def specialist_request_detail(request:HttpRequest, request_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in.", "alert-danger")
        return redirect('accounts:login_view')

    if not Director.objects.filter(user=request.user).exists():
        messages.error(request, "You are not authorized to access this page.", "alert-danger")
        return redirect('core:home_view')
    try:
        specialist_request = SpecialistRequest.objects.get(id=request_id)
        specialist = specialist_request.specialist
        certificates = Certificate.objects.filter(specialist=specialist)
    except SpecialistRequest.DoesNotExist:
        return redirect("core:home_view")
    if request.method == "POST":
        form = SpecialistRequestForm(request.POST,instance=specialist_request)
        if form.is_valid():
            form.save()
            return redirect("directors:specialist_request")
    else:
        form = SpecialistRequestForm(instance=specialist_request)
    return render(request, 'directors/specialist_request_detail.html', {'specialist_request': specialist_request,'specialist': specialist,'certificates': certificates,'form': form})

def specialist_manage(request:HttpRequest):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in.", "alert-danger")
        return redirect('accounts:login_view')

    if not Director.objects.filter(user=request.user).exists():
        messages.error(request, "You are not authorized to access this page.", "alert-danger")
        return redirect('core:home_view')
    specialists = Specialist.objects.filter(specialistrequest__status="approved").distinct()
    return render(request, 'directors/specialist_manage.html', {'specialists': specialists})


def specialist_manage_detail(request:HttpRequest,request_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in.", "alert-danger")
        return redirect('accounts:login_view')

    if not Director.objects.filter(user=request.user).exists():
        messages.error(request, "You are not authorized to access this page.", "alert-danger")
        return redirect('core:home_view')
    try:
        specialist = Specialist.objects.get(id=request_id)
        certificates = Certificate.objects.filter(specialist=specialist)
        plans = SubscriptionPlan.objects.filter(specialist=specialist)
    except Specialist.DoesNotExist:
        return redirect("core:home_view")
    
    return render(request, 'directors/manage_specialist_detail.html', {'specialist': specialist,'certificates': certificates,'plans': plans})

def inactivate_specialist(request:HttpRequest,specialist_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in.", "alert-danger")
        return redirect('accounts:login_view')

    if not Director.objects.filter(user=request.user).exists():
        messages.error(request, "You are not authorized to access this page.", "alert-danger")
        return redirect('core:home_view')
    
    try:
        specialist = Specialist.objects.get(id=specialist_id)
        specialist.user.is_active = False
        specialist.user.save()
        messages.success(request, "Specialist has been inactivated successfully.","alert-success")
    except Specialist.DoesNotExist:
        messages.error(request, "Specialist not found.","alert-danger")
    return redirect('directors:specialist_manage')

def delete_specialist(request:HttpRequest,specialist_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in.", "alert-danger")
        return redirect('accounts:login_view')

    if not Director.objects.filter(user=request.user).exists():
        messages.error(request, "You are not authorized to access this page.", "alert-danger")
        return redirect('core:home_view')
    try:
        specialist = Specialist.objects.get(id=specialist_id)
        specialist.user.delete()
        messages.success(request, "Specialist has been deleted successfully.", "alert-success")
    except Specialist.DoesNotExist:
        messages.error(request, "Specialist not found.","alert-danger")
    return redirect('directors:specialist_manage')

def activate_specialist(request:HttpRequest , specialist_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in.", "alert-danger")
        return redirect('accounts:login_view')

    if not Director.objects.filter(user=request.user).exists():
        messages.error(request, "You are not authorized to access this page.", "alert-danger")
        return redirect('core:home_view')
        
    try:
        specialist = Specialist.objects.get(id=specialist_id)
        specialist.user.is_active = True
        specialist.user.save()
        messages.success(request, "Specialist has been activated successfully.","alert-success")
    except Specialist.DoesNotExist:
        messages.error(request, "Specialist not found.","alert-danger")
    return redirect('directors:specialist_manage')


def approve_specialist_request(request: HttpRequest, request_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in.", "alert-danger")
        return redirect('accounts:login_view')

    if not Director.objects.filter(user=request.user).exists():
        messages.error(request, "You are not authorized to perform this action.", "alert-danger")
        return redirect('core:home_view')

    try:
        specialist_request = SpecialistRequest.objects.get(id=request_id)
    except SpecialistRequest.DoesNotExist:
        messages.error(request, "Request not found.", "alert-danger")
        return redirect('core:home_view')

    if specialist_request.status != SpecialistRequest.RequestStatus.PENDING:
        messages.error(request, "This request has already been processed.", "alert-warning")
        return redirect('directors:Specialist_Request')

    specialist = specialist_request.specialist
    specialist.user.is_active = True
    specialist.user.save()

    specialist_request.status = SpecialistRequest.RequestStatus.APPROVED
    specialist_request.director = Director.objects.get(user=request.user)
    specialist_request.save()

    messages.success(request, "Specialist approved and activated successfully.", "alert-success")
    return redirect('directors:Specialist_Request')

def reject_specialist_request(request: HttpRequest, request_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in.", "alert-danger")
        return redirect('accounts:login_view')

    if not Director.objects.filter(user=request.user).exists():
        messages.error(request, "You are not authorized to perform this action.", "alert-danger")
        return redirect('core:home_view')

    try:
        specialist_request = SpecialistRequest.objects.get(id=request_id)
    except SpecialistRequest.DoesNotExist:
        messages.error(request, "Request not found.", "alert-danger")
        return redirect('core:home_view')

    if specialist_request.status != SpecialistRequest.RequestStatus.PENDING:
        messages.error(request, "This request has already been processed.", "alert-warning")
        return redirect('directors:Specialist_Request')

    if request.method == "POST":
        feedback = request.POST.get('feedback', '')

        specialist_request.status = SpecialistRequest.RequestStatus.REJECTED
        specialist_request.director = Director.objects.get(user=request.user)
        specialist_request.feedback = feedback
        specialist_request.save()

        
        send_mail(
            subject='NutriWay - Specialist Request Rejected',
            message=(
                f"Hello {specialist_request.specialist.user.first_name},\n\n"
                f"Your specialist account request has been rejected.\n"
                f"Reason: {feedback}\n\n"
                "If you have any questions or would like to reapply, feel free to contact us.\n\n"
                "Best regards,\n"
                "NutriWay Support Team"
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[specialist_request.specialist.user.email],
            fail_silently=False,
        )

        messages.success(request, "Specialist request rejected and feedback sent via email.", "alert-success")
        return redirect('directors:Specialist_Request')
    return render(request, 'directors/reject_request.html', {'specialist_request': specialist_request})



