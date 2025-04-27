from django.urls import path
from . import views

app_name = "specialists"

urlpatterns = [
    path('create/subscription/', views.create_subscription_plan, name='create_subscription_plan'),
    path('create/general/', views.create_general_plan, name='create_general_plan'),
    path('plans/subscription/', views.list_subscription_plan, name='list_subscription_plan'),
    path('plans/general/', views.list_general_plan, name='list_general_plan'),
    path('plans/my/', views.my_plans, name='my_plans'),
    path('specialists/', views.all_specialists, name='all_specialists'),
    path('specialist/<int:specialist_id>/', views.specialist_detail, name='specialist_detail'),
    path('specialist/subscriptions', views.specialist_subscriptions, name='specialist_subscriptions'),
    path('create/plan', views.craete_plan, name='craete_plan'),
    path('edit/plan', views.edit_plan, name='edit_plan'),
]