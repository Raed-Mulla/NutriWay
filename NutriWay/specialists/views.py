from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse

def d(request):
  return render(request, "specialists/create_subscription_plan.html")