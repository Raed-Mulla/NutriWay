from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from .models import SpecialistRequest
from .forms import SpecialistRequestForm
from accounts.models import Specialist, Certificate , Director
from specialists.models import SubscriptionPlan
from django.contrib import messages

def specialist_request (request:HttpRequest):
    requests = SpecialistRequest.objects.all()
    return render(request , 'directors/specialist_request.html' , {"requests" : requests})


def specialist_request_detail(request:HttpRequest, request_id):
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
    specialists = Specialist.objects.filter(specialistrequest__status="approved").distinct()
    return render(request, 'directors/specialist_manage.html', {'specialists': specialists})


def specialist_manage_detail(request:HttpRequest,request_id):
    try:
        specialist = Specialist.objects.get(id=request_id)
        certificates = Certificate.objects.filter(specialist=specialist)
        plans = SubscriptionPlan.objects.filter(specialist=specialist)
    except Specialist.DoesNotExist:
        return redirect("core:home_view")
    
    return render(request, 'directors/manage_specialist_detail.html', {'specialist': specialist,'certificates': certificates,'plans': plans})

def inactivate_specialist(request:HttpRequest,specialist_id):
        try:
            specialist = Specialist.objects.get(id=specialist_id)
            specialist.user.is_active = False
            specialist.user.save()
            messages.success(request, "Specialist has been inactivated successfully.","alert-success")
        except Specialist.DoesNotExist:
            messages.error(request, "Specialist not found.","alert-danger")
        return redirect('directors:specialist_manage')

def delete_specialist(request:HttpRequest,specialist_id):
        try:
            specialist = Specialist.objects.get(id=specialist_id)
            specialist.user.delete()
            messages.success(request, "Specialist has been deleted successfully.", "alert-success")
        except Specialist.DoesNotExist:
            messages.error(request, "Specialist not found.","alert-danger")
        return redirect('directors:specialist_manage')

def activate_specialist(request:HttpRequest , specialist_id):
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
        return redirect('director:view_requests')

    specialist = specialist_request.specialist
    specialist.user.is_active = True
    specialist.user.save()

    specialist_request.status = SpecialistRequest.RequestStatus.APPROVED
    specialist_request.director = Director.objects.get(user=request.user)
    specialist_request.save()

    messages.success(request, "Specialist approved and activated successfully.", "alert-success")
    return redirect('director:view_requests')
