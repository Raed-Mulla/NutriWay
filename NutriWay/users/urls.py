from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path('all_my_plans/<int:username>',views.all_my_plans,name='all_my_plans'),
    path('subscription_detail/<int:subscription_id>/', views.subscription_detail , name='subscription_detail'),
    path('subscription_detail/<int:subscription_id>/progress_report/', views.progress_report_view , name='progress_report_view'),
    path('subscription_detail/<int:subscription_id>/check_meals/<int:day_number>',views.check_meals,name='check_meals'),
    path('subscription_detail/view_progress/',views.subscription_progress_view,name='subscription_progress_view'),
    path('subscription_detail/view_progress/<int:progress_report>',views.specialist_comment,'specialist_comment')
]