from django.urls import path
from . import views

app_name = "directors"

urlpatterns = [
    path('specialist/requests/', views.Specialist_Request, name='Specialist_Request'),
    path('specialist/request/<int:request_id>/', views.specialist_request_detail, name='request_detail'),
]