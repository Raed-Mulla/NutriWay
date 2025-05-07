from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
  path("", views.home_view, name="home_view"),
  path('specialist/<int:specialist_id>/add-review/', views.add_review, name='add_review'),
  path("mode/<mode>", views.mode_view, name= "mode_view"),
  path("calorie/calculator", views.calorie_calculator, name= "calorie_calculator"),
  path("review/<int:specialist_id>", views.add_review, name= "add_review"),
  path("about/us", views.about, name= "about"),
]