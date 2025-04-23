from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from .models import SpecialistRequest
from .forms import SpecialistRequestForm
from accounts.models import Specialist, Certificate

def Specialist_Request (request:HttpRequest):
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
    return render(request, 'director/specialist_request_detail.html', {'specialist_request': specialist_request,'specialist': specialist,'certificates': certificates,'form': form})