from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
  path("login/", views.login_view, name="login_view"),
  path("register/user/", views.user_register_view, name="user_register_view"),
  path("register/specialist/", views.specialist_register_view, name="specialist_register_view"),
  path('vertify/',views.vertify_view,name='vertify_view'),
  path('logout/',views.logout_view,name='logout_view'), 
  path('profile/<str:user_name>/', views.profile_view, name='profile_view'),
  path('profile/update/<str:user_name>', views.update_profile_view, name='update_profile_view'),  
 
]
