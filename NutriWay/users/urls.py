from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path('all_my_plans/<int:username>',views.all_my_plans,name='all_my_plans'),
    path('subscription_to_plan/<int:subscriptionPlan_id>',views.subscription_to_plan,name='subscription_to_plan'),
    path('subscription_detail/<int:subscription_id>/', views.subscription_detail , name='subscription_detail'),
    path('subscription_detail/<int:subscription_id>/create/progress_report/', views.create_progress_report_view , name='create_progress_report_view'),
    path('subscription_detail/<int:subscription_id>/check_meals/',views.check_meals,name='check_meals'),
    path('subscription_detail/view_progress/',views.view_progress,name='view_progress'),
]

