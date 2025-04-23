from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse

def home_view(request: HttpRequest):
  return render(request, "core/index.html")

def mode_view(request: HttpRequest, mode):
  next = request.GET.get("next", "/")
  response = redirect(next)

  if mode == "dark":
    response.set_cookie("mode", "dark")
  if mode == "light":
    response.set_cookie("mode", "light")

  return response