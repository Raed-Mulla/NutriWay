from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from .forms import SubscriptionPlanForm , GeneralPlanForm ,SubscriberMealForm, SubscriberPlanForm ,SubscriberMealFormSet
from .models import SubscriptionPlan , Generalplan ,SubscriberMeal,SubscriberPlan,MealCheck
from accounts.models import Specialist , Certificate
from django.contrib import messages
from users.models import Subscription

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

    return render(request, 'specialists/create_subscription_plan.html', {'form': form,'plan_type_choices': SubscriptionPlan.PlanType.choices})




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
    return render(request , 'specialists/list_subscription_plan.html' , {"plans" : plans, "duration_choices":SubscriptionPlan.DurationChoices.choices})

def my_plans(request:HttpRequest):
    specialist = Specialist.objects.get(user=request.user)
    plans = SubscriptionPlan.objects.filter(specialist=specialist)
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
    return render(request, 'specialists/specialist_detail.html', {'specialist': specialist,'certificate': certificate,'plans': plans})

def specialist_subscriptions(request:HttpRequest,plan_id):
    try:
        specialist = Specialist.objects.get(user=request.user)
        subscription_plan = SubscriptionPlan.objects.get(id=plan_id, specialist=specialist)
    except (Specialist.DoesNotExist, SubscriptionPlan.DoesNotExist):
        return redirect('core:home_view')
    
    subscriptions = Subscription.objects.filter(subscription_plan=subscription_plan)
    return render(request, 'specialists/view_subscriptions.html', {'subscriptions': subscriptions, 'subscription_plan': subscription_plan})


def create_subscriber_plan(request:HttpRequest, subscription_id):
    try:
        specialist = Specialist.objects.get(user=request.user)
        subscription = Subscription.objects.get(id=subscription_id, subscription_plan__specialist=specialist)
    except (Specialist.DoesNotExist, Subscription.DoesNotExist):
        return redirect('core:home_view')

    if request.method == "POST":
        plan_form = SubscriberPlanForm(request.POST)
        meal_formset = SubscriberMealFormSet(request.POST)

        if plan_form.is_valid() and meal_formset.is_valid():
            subscriber_plan = plan_form.save(commit=False)
            subscriber_plan.specialist = specialist
            subscriber_plan.save()

            subscription.subscriber_plan = subscriber_plan
            subscription.save()

            meals = meal_formset.save(commit=False)
            for meal in meals:
                meal.subscriber_plan = subscriber_plan
                meal.save()

            return redirect('specialists:my_plans')

    else:
        plan_form = SubscriberPlanForm()
        meal_formset = SubscriberMealFormSet(queryset=SubscriberMeal.objects.none())

    return render(request, 'specialists/create_subscriber_plan.html', {'plan_form': plan_form,'meal_formset': meal_formset,'subscription': subscription})


def edit_subscriber_plan(request:HttpRequest, plan_id):
    try:
        subscriber_plan = SubscriberPlan.objects.get(id=plan_id, specialist__user=request.user)
    except SubscriberPlan.DoesNotExist:
        return redirect("core:home_view")
    
    meal_formset = SubscriberMealFormSet(queryset=SubscriberMeal.objects.filter(subscriber_plan=subscriber_plan))

    if request.method == "POST":
        meal_formset = SubscriberMealFormSet(request.POST, queryset=SubscriberMeal.objects.filter(subscriber_plan=subscriber_plan))
        if meal_formset.is_valid():
            meals = meal_formset.save(commit=False)
            for meal in meals:
                meal.subscriber_plan = subscriber_plan
                meal.save()
            return redirect('specialists:my_plans')

    return render(request, 'specialists/edit_subscriber_plan.html', {'meal_formset': meal_formset,'subscriber_plan': subscriber_plan})

def specialist_subscriptions(request:HttpRequest,plan_id):
    try:
        specialist = Specialist.objects.get(user=request.user)
        subscription_plan = SubscriptionPlan.objects.get(id=plan_id, specialist=specialist)
    except (Specialist.DoesNotExist, SubscriptionPlan.DoesNotExist):
        return redirect('core:home_view')
    
    subscriptions = Subscription.objects.filter(subscription_plan=subscription_plan)
    return render(request, 'specialists/view_subscriptions.html', {'subscriptions': subscriptions, 'subscription_plan': subscription_plan})


def create_subscriber_plan(request:HttpRequest, subscription_id):
    try:
        specialist = Specialist.objects.get(user=request.user)
        subscription = Subscription.objects.get(id=subscription_id, subscription_plan__specialist=specialist)
    except (Specialist.DoesNotExist, Subscription.DoesNotExist):
        return redirect('core:home_view')

    if request.method == "POST":
        plan_form = SubscriberPlanForm(request.POST)
        meal_formset = SubscriberMealFormSet(request.POST)

        if plan_form.is_valid() and meal_formset.is_valid():
            subscriber_plan = plan_form.save(commit=False)
            subscriber_plan.specialist = specialist
            subscriber_plan.save()

            subscription.subscriber_plan = subscriber_plan
            subscription.save()

            meals = meal_formset.save(commit=False)
            for meal in meals:
                meal.subscriber_plan = subscriber_plan
                meal.save()

            return redirect('specialists:my_plans')

    else:
        plan_form = SubscriberPlanForm()
        meal_formset = SubscriberMealFormSet(queryset=SubscriberMeal.objects.none())

    return render(request, 'specialists/create_subscriber_plan.html', {'plan_form': plan_form,'meal_formset': meal_formset,'subscription': subscription})


def edit_subscriber_plan(request:HttpRequest, plan_id):
    try:
        subscriber_plan = SubscriberPlan.objects.get(id=plan_id, specialist__user=request.user)
    except SubscriberPlan.DoesNotExist:
        return redirect("core:home_view")
    
    meal_formset = SubscriberMealFormSet(queryset=SubscriberMeal.objects.filter(subscriber_plan=subscriber_plan))

    if request.method == "POST":
        meal_formset = SubscriberMealFormSet(request.POST, queryset=SubscriberMeal.objects.filter(subscriber_plan=subscriber_plan))
        if meal_formset.is_valid():
            meals = meal_formset.save(commit=False)
            for meal in meals:
                meal.subscriber_plan = subscriber_plan
                meal.save()
            return redirect('specialists:my_plans')

    return render(request, 'specialists/edit_subscriber_plan.html', {'meal_formset': meal_formset,'subscriber_plan': subscriber_plan})

