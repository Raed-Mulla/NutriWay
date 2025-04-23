from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from .forms import SubscriptionPlanForm , GeneralPlanForm
from .models import SubscriptionPlan , Generalplan
from accounts.models import Specialist , Certificate
from django.contrib import messages

def create_subscription_plan(request: HttpRequest):
    if request.method == "POST":
        form = SubscriptionPlanForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                subscription_plan = form.save(commit=False)
                subscription_plan.specialist = Specialist.objects.get(user=request.user)
                subscription_plan.save()
                messages.success(request, "Subscription plan created successfully." ,"alert-success")
                return redirect("core:home_view")
            except Exception as e:
                messages.error(request, "Failed to save the subscription plan." , "alert-danger")
        else:
            messages.error(request, "Please correct the errors in the form." , "alert-danger")
    else:
        form = SubscriptionPlanForm()

    return render(request, 'specialists/create_subscription_plan.html', {'form': form})




def create_general_plan(request: HttpRequest):
    if request.method == "POST":
        form = GeneralPlanForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                general_plan = form.save(commit=False)
                general_plan.specialist = Specialist.objects.get(user=request.user)
                general_plan.save()
                messages.success(request, "General plan created successfully.","alert-success")
                return redirect("core:home_view")
            except Exception as e:
                messages.error(request, "Failed to create general plan." , "alert-danger")
        else:
            messages.error(request, "Please correct the errors in the form." , "alert-danger")
    else:
        form = GeneralPlanForm()
    
    return render(request, 'specialists/create_general_plan.html', {'form': form})


def list_general_plan (request:HttpRequest):
    plans = Generalplan.objects.all()
    return render(request , 'specialists/list_general_plan.html' , {"plans" : plans})

def list_subscription_plan (request:HttpRequest):
    plans = SubscriptionPlan.objects.all()
    return render(request , 'specialists/list_subscription_plan.html' , {"plans" : plans})

def my_plans(request:HttpRequest):
    specialist = Specialist.objects.get(user=request.user)
    plans = SubscriptionPlan.objects.filter(Specialist=specialist)
    return render(request,'specialists/my_plans.html',{'plans' : plans})


def all_specialists(request:HttpRequest):
    specialists = Specialist.objects.all()
    return render(request, 'specialists/specialists_list.html', {'specialists': specialists})

def specialist_detail(request:HttpRequest , specialist_id):
    try:
        specialist = Specialist.objects.get(id=specialist_id)
        certificate = Certificate.objects.filter(specialist=specialist)
        plans = SubscriptionPlan.objects.filter(specialist=specialist)
    except Specialist.DoesNotExist:
        return redirect("core:home_view")
    return render(request, 'public/specialist_detail.html', {'specialist': specialist,'certificate': certificate,'plans': plans})

