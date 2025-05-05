from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from .models import SpecialistRequest
from .forms import SpecialistRequestForm
from accounts.models import Specialist, Certificate , Director , Person
from specialists.models import SubscriptionPlan ,Generalplan
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from users.models import Subscription , GeneralPlanPurchase
from django.db.models import Count , Sum , Value,F , FloatField
from django.utils.timezone import now
from django.db.models.functions import TruncDate , TruncMonth , Coalesce
from django.contrib.auth import get_user_model
from directors.models import SpecialistRequest
from collections import defaultdict
from calendar import month_name
import json



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


def director_dashboard(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'director'):
        messages.error(request, "You are not authorized to view this page.")
        return redirect("core:home_view")

    today = now().date()
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    User = get_user_model()

    # المستخدمين الجدد هذا الشهر
    new_users = (
        User.objects.filter(date_joined__date__gte=start_of_month)
        .annotate(date=TruncDate('date_joined'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    dates = [str(entry['date']) for entry in new_users]
    counts = [entry['count'] for entry in new_users]

    # المستخدمين الجدد هذا العام
    users_year = (
        User.objects.filter(date_joined__date__gte=start_of_year)
        .annotate(month=TruncMonth('date_joined'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    monthly_labels = [entry['month'].strftime('%B') for entry in users_year]
    monthly_counts = [entry['count'] for entry in users_year]

    # الاشتراكات الجديدة شهريًا
    subscriptions_by_month = (
        Subscription.objects.filter(created_at__date__gte=start_of_year)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    subscription_chart_labels = [entry['month'].strftime('%B') for entry in subscriptions_by_month]
    subscription_chart_counts = [entry['count'] for entry in subscriptions_by_month]

    # حساب أرباح واشتراكات الأخصائيين
    duration_map = {
        '1_month': 1,
        '3_months': 3,
        '6_months': 6,
        '12_months': 12
    }

    specialist_stats = defaultdict(lambda: {'username': '', 'total': 0.0, 'subscriber_count': 0})

    for sub in Subscription.objects.filter(status='active'):
        months = duration_map.get(sub.duration, 1)
        earnings = sub.subscription_plan.price * months
        sid = sub.subscription_plan.specialist.id
        username = sub.subscription_plan.specialist.user.username

        specialist_stats[sid]['username'] = username
        specialist_stats[sid]['total'] += earnings
        specialist_stats[sid]['subscriber_count'] += 1

    for entry in GeneralPlanPurchase.objects.all():
        sid = entry.general_plan.specialist.id
        username = entry.general_plan.specialist.user.username
        price = entry.general_plan.price

        specialist_stats[sid]['username'] = username
        specialist_stats[sid]['total'] += price

    top_earning_specialists = sorted(specialist_stats.values(), key=lambda x: x['total'], reverse=True)[:5]
    top_subscribed_specialists = sorted(specialist_stats.values(), key=lambda x: x['subscriber_count'], reverse=True)[:5]

    pending_requests_count = SpecialistRequest.objects.filter(status='pending').count()

    context = {
        'total_general_plans': Generalplan.objects.count(),
        'total_subscription_plans': SubscriptionPlan.objects.count(),
        'total_specialists': Specialist.objects.count(),
        'total_persons': Person.objects.count(),
        'pending_requests_count': pending_requests_count,
        'dates': dates,
        'counts': counts,
        'monthly_labels': monthly_labels,
        'monthly_counts': monthly_counts,
        'subscription_chart_labels': subscription_chart_labels,
        'subscription_chart_counts': subscription_chart_counts,
        'top_earning_specialists': top_earning_specialists,
        'top_subscribed_specialists': top_subscribed_specialists,
    }

    return render(request, 'directors/dashboard.html', context)