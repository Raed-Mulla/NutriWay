from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from specialists.models import Specialist
from django.contrib import messages
from accounts.models import Person
from specialists.models import *
from .models import Subscription,ProgressReport
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta


@login_required
def my_plans(request: HttpRequest):
    try:
        person = Person.objects.get(user=request.user)
        subscriptions = Subscription.objects.filter(person=person)
        return render(request, 'users/my_plans.html', {'subscriptions': subscriptions})
    except Person.DoesNotExist:
        messages.error(request, "User profile not found", "alert-danger")
        return redirect('core:home_view')

@login_required
def subscription_to_plan(request: HttpRequest, plan_id: int):
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)
        person = Person.objects.get(user=request.user)
        
        if Subscription.objects.filter(person=person, subscription_plan=plan, status='active').exists():
            messages.warning(request, "You are already subscribed to this plan", "alert-warning")
            return redirect('users:my_plans')
        
        duration_map = {
            '1_month': 30,
            '3_months': 90,
            '6_months': 180,
            '12_months': 365
        }
        start_date = datetime.now().date()
        days = duration_map.get(plan.duration, 30)  
        end_date = start_date + timedelta(days=days)
        
        # subscriber_plan = SubscriberPlan.objects.create(
        #     specialist=plan.specialist,
        #     name=f"{person.user.username}'s {plan.name}",
        #     description=f"Custom plan for {person.user.username} based on {plan.name}"
        # )
        
        subscription = Subscription.objects.create(
            person=person,
            subscription_plan=plan,
            # subscriber_plan=subscriber_plan,
            start_date=start_date,
            end_date=end_date,
            status='active'
        )
        
        messages.success(request, "Successfully subscribed to the plan", "alert-success")
        return redirect('users:subscription_detail', subscription_id=subscription.id)
    
    except SubscriptionPlan.DoesNotExist:
        messages.error(request, "Plan not found", "alert-danger")
    except Person.DoesNotExist:
        messages.error(request, "User profile not found", "alert-danger")
    except Exception as e:
        messages.error(request, f"Error subscribing to plan: {str(e)}", "alert-danger")
    
    return redirect('specialists:list_subscription_plan')

@login_required
def subscription_detail(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    
    if (request.user != subscription.person.user and 
        request.user != subscription.subscription_plan.specialist.user):
        messages.error(request, "You don't have permission to view this subscription", "alert-danger")
        return redirect('users:my_plans')
    
    plan = subscription.subscription_plan
    specialist = plan.specialist
    
    today = datetime.now().date()
    days_elapsed = (today - subscription.start_date).days + 1
    total_days = (subscription.end_date - subscription.start_date).days
    days_remaining = max(0, (subscription.end_date - today).days)
    progress_percentage = min(100, int((days_elapsed / total_days) * 100)) if total_days > 0 else 0
    
    today_meals = SubscriberMeal.objects.filter(
        subscriber_plan=subscription.subscriber_plan,
        day_number=days_elapsed
    )
    
    
    progress_reports_list = list(ProgressReport.objects.filter(
        subscription=subscription.subscription_plan
    ).order_by('-date')[:5])
    
    weight_progress = None
    if len(progress_reports_list) >= 2:
        latest_weight = progress_reports_list[0].weight
        first_weight = progress_reports_list[-1].weight
        weight_change = latest_weight - first_weight
        weight_progress = {
            'first': first_weight,
            'latest': latest_weight,
            'change': weight_change,
            'is_positive': weight_change > 0
        }
    
    subscription_detail = {
        'subscription': subscription,
        'subscription_id':subscription_id,
        'plan': plan,
        'specialist': specialist,
        'days_elapsed': days_elapsed,
        'days_remaining': days_remaining,
        'total_days': total_days,
        'progress_percentage': progress_percentage,
        'today_meals': today_meals,
        'progress_reports': progress_reports_list, 
        'weight_progress': weight_progress,
        'is_specialist': hasattr(request.user, 'specialist'),
    }
    
    return render(request, 'users/subscription_detail.html', subscription_detail)

@login_required
def create_progress_report_view(request:HttpRequest,subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    
    if subscription.person.user != request.user:
        messages.error(request, "You don't have permission to add progress for this subscription", "alert-danger")
        return redirect('users:my_plans')
    
    if request.method == 'POST':
        try:
            weight = float(request.POST.get('weight'))
            note = request.POST.get('note', '')
            
            ProgressReport.objects.create(
                subscription=subscription.subscription_plan,
                date=datetime.now().date(),
                weight=float(weight),
                note=note
            )
            
            messages.success(request, "Progress report added successfully", "alert-success")
            return redirect('users:subscription_detail', subscription_id=subscription.id)
        
        except ValueError:
            messages.error(request, "Please enter a valid weight", "alert-danger")
            messages.error(request, f'weight (type:{type(weight)})' , "alert-danger")

        except Exception as e:
            messages.error(request, f"Error adding progress: {str(e)}", "alert-danger")
    
    return render(request, 'users/create_progress_report.html', {'subscription': subscription,'subscription_id': subscription_id})
@login_required
def check_meals(request: HttpRequest, subscription_id):
    pass

def view_progress(request:HttpRequest, subscription_id):
    progress_reports = ProgressReport.objects.filter(subscription= subscription_id)
    return render(request,'users/view_progress.html',{'progress_reports' : progress_reports, 'subscription_id': subscription_id})

@login_required
def cancel_subscription(request: HttpRequest, subscription_id: int):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    
    if not hasattr(request.user, 'specialist') or subscription.subscription_plan.specialist.user != request.user:
        messages.error(request, "Only specialists can cancel subscriptions", "alert-danger")
        return redirect('core:home_view')
    
    subscription.status = 'cancelled'
    subscription.save()
    messages.success(request, "Subscription cancelled successfully", "alert-success")
    # return redirect('specialists:dashboard')  
    return redirect('users:subscription_detail',subscription_id )