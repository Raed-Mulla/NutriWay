from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path('start-checkout/<int:plan_id>/', views.start_checkout_subscription, name='start_checkout_subscription'),
    path('start-checkout-general/<int:plan_id>/', views.start_checkout_general, name='start_checkout_general'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('general-success/', views.payment_success_general, name='payment_success_general'),
    path('general-cancel/', views.payment_cancel_general, name='payment_cancel_general'),

]