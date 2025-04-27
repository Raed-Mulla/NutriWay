from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse

from accounts.models import Person , Specialist
from .models import Review
from .forms import ReviewForm
from django.contrib import messages


def add_review(request:HttpRequest , specialist_id):
  try:
    specialist = Specialist.objects.get(id=specialist_id)
    person = Person.objects.get(user=request.user)
  except (Specialist.DoesNotExist, Person.DoesNotExist):
    return redirect("core:home_view")
  
  if Review.objects.filter(person=person, specialist=specialist).exists():
    messages.warning(request, "You have already submitted a review.")
    return redirect("core:home_view")
  
  if request.method == "POST":
    form = ReviewForm(request.POST)
    if form.is_valid():
      review = form.save(commit=False)
      review.person = person
      review.specialist = specialist
      review.save()
      messages.success(request, "Your review has been submitted successfully." , "alert-success")
      return redirect('core:home_view')
  else:
    form = ReviewForm()

  return render(request,'core/add_review.html' , {'form' : form , 'specialist' : specialist})


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

