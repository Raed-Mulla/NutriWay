from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path('my_plans/', views.my_plans_view, name='my_plans_view'),
    path('subscribe/<int:subscriptionPlan_id>/', views.subscription_to_plan, name='subscription_to_plan'),
    path('subscription/<int:subscription_id>/', views.subscription_detail, name='subscription_detail'),
    path('subscription/<int:subscription_id>/progress/create/', views.create_progress_report_view, name='create_progress_report_view'),
    path('subscription/<int:subscription_id>/meals/history/', views.meal_history, name='meal_history'),
    path('subscription/<int:subscription_id>/meals/update/<int:day_number>/', views.update_meal_day, name='update_meal_day'),
    path('subscription/<int:subscription_id>/progress/', views.view_progress, name='view_progress'),
    # path('subscription/<int:subscription_id>/cancel/', views.cancel_subscription, name='cancel_subscription'),
]