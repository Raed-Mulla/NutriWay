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
    path('plans/my/<int:plan_id>/subscriptions/', views.specialist_subscriptions, name='specialist_subscriptions'),
    path('subscriber/create/<int:subscription_id>/', views.create_subscriber_plan, name='create_subscriber_plan'),
    path('subscriber/edit/<int:plan_id>/', views.edit_subscriber_plan, name='edit_subscriber_plan'),
    path('subscriptions/<int:subscription_id>/progress/', views.add_comment, name='add_comment'),
    path('subscriptions/delete/<int:subscription_id>/', views.delete_subscription, name="delete_subscription"),
    path('certificate/specialization/<int:specialist_id>/', views.show_certificate_specialization, name='show_specialization_certificate_certificate'),
    path('certificates/<int:specialist_id>/', views.show_certificate, name='show_certificates'),
    path('specialist/<int:specialist_id>/dashboard/', views.specialist_dashboard, name='specialist_dashboard'),
    path('general/<int:plan_id>/detail/', views.general_plan_detail_view, name='general_plan_detail'),
    path('subscription/<int:plan_id>/detail/', views.subscription_plan_detail_view, name='subscription_plan_detail_view'),
]