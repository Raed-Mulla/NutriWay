from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from specialists.models import Specialist
from django.contrib import messages
from accounts.models import Person , Director
from specialists.models import *
from .models import Subscription, ProgressReport
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from itertools import groupby
from datetime import date


def my_plans(request: HttpRequest):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to access this page.", "alert-danger")
        return redirect("accounts:login_view")
    if not hasattr(request.user, 'person'):
        messages.error(request, "You must be a user to view this page", "alert-danger")
        return redirect('core:home_view')
    try:
        person = Person.objects.get(user=request.user)
        subscriptions = Subscription.objects.filter(person=person)
        if (request.user != person.user):
            messages.error(request, "You don't have permission to view this subscription", "alert-danger")
            return redirect('users:my_plans')
        today = datetime.now().date()
        for subscription in subscriptions:
            if today > subscription.end_date:
                subscription.status = subscription.StatusChoices.EXPIRED
                subscription.save()
                
        return render(request, 'users/my_plans.html', {'subscriptions': subscriptions})
    except Person.DoesNotExist:
        messages.error(request, "User profile not found", "alert-danger")
        return redirect('core:home_view')


def subscription_to_plan(request: HttpRequest, plan_id: int,duration: str):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to access this page.", "alert-danger")
        return redirect("accounts:login_view")
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)
        if Specialist.objects.filter(user=request.user).exists() or Director.objects.filter(user=request.user).exists() or request.user.is_staff:
            messages.error(request, "You are not allowed to subscribe to plans.", "alert-danger")
            return redirect('specialists:list_subscription_plan')
        person = Person.objects.get(user=request.user)

        if Subscription.objects.filter(person=person, subscription_plan=plan, status='active').exists():
            messages.warning(request, "You are already subscribed to this plan.", "alert-warning")
            return redirect('users:my_plans')
        
        duration_map = {
            '1_month': 30,
            '3_months': 90,
            '6_months': 180,
            '12_months': 365
        }
        start_date = datetime.now().date()
        days = duration_map.get(duration, 30)  
        end_date = start_date + timedelta(days=days)
        
        
        subscription = Subscription.objects.create(
            person=person,
            subscription_plan=plan,
            start_date=start_date,
            end_date=end_date,
            duration=duration,
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


def subscription_detail(request, subscription_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to access this page.", "alert-danger")
        return redirect("accounts:login_view")
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
    
    # Check which day to display
    display_day = days_elapsed
    display_date = today
    day_param = request.GET.get('day')
    
    if day_param:
        try:
            day_number = int(day_param)
            if 1 <= day_number <= days_elapsed:
                display_day = day_number
                display_date = subscription.start_date + timedelta(days=day_number-1)
        except ValueError:
            # If invalid day param, use current day
            pass
    
    # Handle meal checking (POST request)
    if request.method == 'POST' and request.user == subscription.person.user:
        check_date = today
        day_number = days_elapsed
        
        if 'check_day' in request.POST:
            try:
                day_number = int(request.POST.get('check_day'))
                if 1 <= day_number <= days_elapsed:
                    # Calculate the date for this day number
                    check_date = subscription.start_date + timedelta(days=day_number-1)
                else:
                    messages.error(request, "Invalid day selected", "alert-danger")
                    return redirect('users:subscription_detail', subscription_id=subscription.id)
            except ValueError:
                messages.error(request, "Invalid day format", "alert-danger")
                return redirect('users:subscription_detail', subscription_id=subscription.id)
        
        day_meals = SubscriberMeal.objects.filter(
            subscriber_plan=subscription.subscriber_plan,
            day_number=day_number
        )
        
        checked_meal_ids = request.POST.getlist('checked_meals', [])
        checked_meal_ids = [int(meal_id) for meal_id in checked_meal_ids if meal_id.isdigit()]
        
        for meal in day_meals:
            is_checked = meal.id in checked_meal_ids
            
            meal_check, created = MealCheck.objects.get_or_create(
                subscription=subscription,
                subscriber_meal=meal,
                date=check_date,
                defaults={'is_checked': is_checked}
            )
            
            if not created:
                meal_check.is_checked = is_checked
                meal_check.save()
        
        messages.success(request, f"Meal progress for day {day_number} updated", "alert-success")
        return redirect('users:subscription_detail', subscription_id=subscription.id)
    
    day_meals = SubscriberMeal.objects.filter(
        subscriber_plan=subscription.subscriber_plan,
        day_number=display_day
    )
    
    meal_checks = MealCheck.objects.filter(
        subscription=subscription,
        subscriber_meal__in=day_meals,
        date=display_date
    )
    
    available_days = []
    for day in range(1, days_elapsed + 1):
        day_date = subscription.start_date + timedelta(days=day-1)
        available_days.append({
            'number': day,
            'date': day_date,
            'is_current': day == display_day
        })
    
    progress_reports_list = list(ProgressReport.objects.filter(
        subscription=subscription
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
    
    today_checked = MealCheck.objects.filter(
        subscription=subscription,
        date=today
    ).exists()
    if subscription.subscriber_plan:
        subscriber_plan = subscription.subscriber_plan
    else:
        subscriber_plan = None
    subscription_detail = {
        'subscription': subscription,
        'subscription_id': subscription_id,
        'plan': plan,
        'specialist': specialist,
        'days_elapsed': days_elapsed,
        'days_remaining': days_remaining,
        'total_days': total_days,
        'progress_percentage': progress_percentage,
        'day_meals': day_meals,
        'meal_checks': meal_checks,
        'progress_reports': progress_reports_list, 
        'weight_progress': weight_progress,
        'is_specialist': hasattr(request.user, 'specialist'),
        'display_day': display_day,
        'display_date': display_date,
        'available_days': available_days,
        'today_checked': today_checked,
        'subscriber_plan':subscriber_plan,
    }
    
    return render(request, 'users/subscription_detail.html', subscription_detail)

def create_progress_report_view(request:HttpRequest,subscription_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to access this page.", "alert-danger")
        return redirect("accounts:login_view")
    subscription = get_object_or_404(Subscription, id=subscription_id)
    if subscription.person.user != request.user and subscription.subscription_plan.specialist.user != request.user:
        messages.error(request, "You don't have permission to view progress for this subscription", "alert-danger")
        return redirect('core:home_view')
    if subscription.StatusChoices.CANCELLED == subscription.status:
        messages.error(request, "Your subscription is cancelled. ", "alert-danger")
        return redirect('users:my_plans')
    if subscription.person.user != request.user:
        messages.error(request, "You don't have permission to add progress for this subscription", "alert-danger")
        return redirect('users:my_plans')
    
    if request.method == 'POST':
        try:

            weight = request.POST.get('weight')
            note = request.POST.get('note', '')
            
            ProgressReport.objects.create(
                subscription=subscription,
                date=datetime.now().date(),
                weight=float(weight),
                note=note
            )
            
            messages.success(request, "Progress report added successfully", "alert-success")
            return redirect('users:subscription_detail', subscription_id=subscription.id)
        
        except ValueError as e:
            messages.error(request, e , "alert-danger")
            messages.error(request, "Please enter a valid weight", "alert-danger")

        except Exception as e:
            messages.error(request, f"Error adding progress: {str(e)}", "alert-danger")
    
    return render(request, 'users/create_progress_report.html', {'subscription': subscription,'subscription_id': subscription_id})

def view_progress(request:HttpRequest, subscription_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to access this page.", "alert-danger")
        return redirect("accounts:login_view")
    subscription = get_object_or_404(Subscription, id=subscription_id)   
    if subscription.person.user != request.user and subscription.subscription_plan.specialist.user != request.user:
        messages.error(request, "You don't have permission to view progress for this subscription", "alert-danger")
        return redirect('core:home_view')
    progress_reports = ProgressReport.objects.filter(subscription= subscription_id)
    is_cancelled = subscription.status == subscription.StatusChoices.CANCELLED
    return render(request,'users/view_progress.html',{'progress_reports' : progress_reports, 'subscription_id': subscription_id,'is_cancelled':is_cancelled})

# @login_required
# def cancel_subscription(request: HttpRequest, subscription_id: int):
#     subscription = get_object_or_404(Subscription, id=subscription_id)
    
#     if not hasattr(request.user, 'specialist') or subscription.subscription_plan.specialist.user != request.user:
#         messages.error(request, "Only specialists can cancel subscriptions", "alert-danger")
#         return redirect('core:home_view')
    
#     subscription.status = 'cancelled'
#     subscription.save()
#     messages.success(request, "Subscription cancelled successfully", "alert-success")
#     return redirect('users:subscription_detail',subscription_id)


def meal_history(request, subscription_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to access this page.", "alert-danger")
        return redirect("accounts:login_view")
    subscription = get_object_or_404(Subscription, id=subscription_id)
    
    if (request.user != subscription.person.user and 
        request.user != subscription.subscription_plan.specialist.user):
        messages.error(request, "You don't have permission to view this subscription", "alert-danger")
        return redirect('users:my_plans')
    
    meal_checks = MealCheck.objects.filter(
        subscription=subscription
    ).select_related('subscriber_meal').order_by('-date')
    
    total_meals = meal_checks.count()
    checked_count = meal_checks.filter(is_checked=True).count()
    not_checked_count = total_meals - checked_count
    
    compliance_rate = 0
    if total_meals > 0:
        compliance_rate = round((checked_count / total_meals) * 100)
    
    today_date = date.today()
    
    all_subscriber_meals = SubscriberMeal.objects.filter(
        subscriber_plan=subscription.subscriber_plan
    ).order_by('day_number', 'meal_type')
    
    if not all_subscriber_meals.exists():
        meal_data = {
            'subscription': subscription,
            'total_meals': 0,
            'checked_count': 0,
            'not_checked_count': 0,
            'compliance_rate': 0,
            'grouped_months': [],
            'today_date': today_date,
            'is_specialist': hasattr(request.user, 'specialist'),
            'no_meals': True
        }
        return render(request, 'users/meal_history.html', meal_data)
    
    # Get all dates that have meals assigned (past, present, and future)
    start_date = subscription.start_date
    if hasattr(start_date, 'date'):
        start_date = start_date.date()
    
    end_date = subscription.end_date
    if hasattr(end_date, 'date'):
        end_date = end_date.date()
    
    # Get unique day numbers from meal plan
    day_numbers = all_subscriber_meals.values_list('day_number', flat=True).distinct().order_by('day_number')
    
    # Generate all dates for the subscription period
    all_dates = []
    for day_number in day_numbers:
        day_date = start_date + timedelta(days=day_number - 1)
        if day_date <= end_date:  # Only include dates within subscription period
            all_dates.append(day_date)
    
    # Function to group by month
    def get_month_key(d):
        return date(d.year, d.month, 1)
    
    # Sort all dates by month
    all_dates.sort(reverse=True)  # Most recent first
    
    # Group by month
    grouped_months = []
    for month, month_dates in groupby(all_dates, get_month_key):
        month_dates = list(month_dates)
        month_dates.sort(reverse=True)  # Sort dates within month in descending order
        
        days = []
        for day_date in month_dates:
            # Calculate day number from date
            day_number = (day_date - start_date).days + 1
            
            # Get meals for this day number
            day_subscriber_meals = all_subscriber_meals.filter(day_number=day_number)
            
            # Get meal checks for this date if it's today or in the past
            day_meal_checks = meal_checks.filter(date=day_date) if day_date <= today_date else []
            
            day_meals = []
            
            # Add all meals for this day with their check status
            for meal in day_subscriber_meals:
                # Find the corresponding check for this meal on this date
                meal_check = next((check for check in day_meal_checks if check.subscriber_meal_id == meal.id), None)
                
                is_checked = False
                if meal_check:
                    is_checked = meal_check.is_checked
                
                day_meals.append({
                    'meal': meal,
                    'is_checked': is_checked,
                    'is_past_or_today': day_date <= today_date
                })
            
            # Only add days that have meals
            if day_meals:
                days.append({
                    'number': day_number,
                    'date': day_date,
                    'meals': day_meals,
                    'is_future': day_date > today_date,
                    'is_today': day_date == today_date
                })
        
        if days:  # Only add months that have days with meals
            grouped_months.append((month, days))
    
    is_specialist = hasattr(request.user, 'specialist')
    meal_data = {
        'subscription': subscription,
        'total_meals': total_meals,
        'checked_count': checked_count,
        'not_checked_count': not_checked_count,
        'compliance_rate': compliance_rate,
        'grouped_months': grouped_months,
        'today_date': today_date,
        'is_specialist': is_specialist,
    }
    return render(request, 'users/meal_history.html', meal_data)

@login_required
def update_meal_day(request, subscription_id, day_number):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    
    if request.user != subscription.person.user:
        messages.error(request, "You don't have permission to update this subscription", "alert-danger")
        return redirect('users:my_plans')
    
    if request.method == 'POST':
        # Calculate the date for this day number
        start_date = subscription.start_date
        if hasattr(start_date, 'date'):
            start_date = start_date.date()
            
        day_date = start_date + timedelta(days=day_number-1)
        
        # Don't allow updating future days
        today = datetime.now().date()
        if day_date > today:
            messages.error(request, "You cannot update future days", "alert-danger")
            return redirect('users:meal_history', subscription_id=subscription.id)
        
        # Get meals for the selected day
        day_meals = SubscriberMeal.objects.filter(
            subscriber_plan=subscription.subscriber_plan,
            day_number=day_number
        )
        
        # Get checked meal IDs from form
        checked_meal_ids = request.POST.getlist('checked_meals', [])
        checked_meal_ids = [int(meal_id) for meal_id in checked_meal_ids if meal_id.isdigit()]
        
        # Update meal checks
        for meal in day_meals:
            is_checked = meal.id in checked_meal_ids
            
            meal_check, created = MealCheck.objects.get_or_create(
                subscription=subscription,
                subscriber_meal=meal,
                date=day_date,
                defaults={'is_checked': is_checked}
            )
            
            if not created:
                meal_check.is_checked = is_checked
                meal_check.save()
        
        messages.success(request, f"Meal progress for Day {day_number} updated successfully!", "alert-success")
    
    return redirect('users:meal_history', subscription_id=subscription.id)