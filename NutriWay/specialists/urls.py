from django.urls import path
from . import views

app_name = "specialists"

urlpatterns = [
  path("p", views.d)
]