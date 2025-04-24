from django.urls import path
from . import views

app_name = "directors"

urlpatterns = [
    path('specialist/requests/', views.specialist_request, name='Specialist_Request'),
    path('specialist/request/<int:request_id>/', views.specialist_request_detail, name='request_detail'),
    path('specialists/manage/', views.specialist_manage, name='specialist_manage'),
    path('specialists/manage/<int:request_id>/', views.specialist_manage_detail, name='specialist_manage_detail'),
    path('specialist/<int:specialist_id>/inactivate/', views.inactivate_specialist, name='inactivate_specialist'),
    path('specialist/<int:specialist_id>/delete/', views.delete_specialist, name='delete_specialist'),
    path('specialist/<int:specialist_id>/activate/', views.activate_specialist, name='activate_specialist'),
]