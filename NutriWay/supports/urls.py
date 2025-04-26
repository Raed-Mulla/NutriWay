from django.urls import path
from . import views

app_name = "supports"

urlpatterns = [
    path('contact/', views.contact_us_view, name='contact_us'),
]