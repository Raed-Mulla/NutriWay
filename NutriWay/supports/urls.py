from django.urls import path
from . import views

app_name = "supports"

urlpatterns = [
    path('contact/', views.contact_us_view, name='contact_us'),
    path('messages/', views.contact_messages, name='contact_messages'),
    path('messages/resolve/<int:message_id>/', views.mark_as_resolved, name='mark_as_resolved'),

]