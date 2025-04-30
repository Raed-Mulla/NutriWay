from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from accounts.models import Person , Specialist
from .models import Review
from .forms import ReviewForm
from django.contrib import messages
from users.models import Subscription
from specialists.models import Specialist , Generalplan , SubscriptionPlan
from django.db.models import Avg , Max


def add_review(request:HttpRequest , specialist_id):
  try:
    specialist = Specialist.objects.get(id=specialist_id)
    person = Person.objects.get(user=request.user)
  except (Specialist.DoesNotExist, Person.DoesNotExist):
    return redirect("core:home_view")
  
  if not Subscription.objects.filter(person=person, subscription_plan__specialist=specialist).exists():
    messages.error(request, "You must be subscribed to this specialist to leave a review.", "alert-danger")
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
  top_specialist = Specialist.objects.annotate(average_rating=Avg('reviews__rating')).order_by('-average_rating')[:3]
  general_plan = Generalplan.objects.all()[:3]
  subscription_plan = SubscriptionPlan.objects.all()[:3]
  reviews = Review.objects.select_related('person','specialist').order_by('-rating')[:10]
  return render(request, "core/index.html", {"top_specialist":top_specialist , "general_plan" : general_plan , "subscription_plan" : subscription_plan , 'reviews' : reviews, "DurationChoices":SubscriptionPlan.DurationChoices.choices})

def mode_view(request: HttpRequest, mode):
  next = request.GET.get("next", "/")
  response = redirect(next)

  if mode == "dark":
    response.set_cookie("mode", "dark")
  if mode == "light":
    response.set_cookie("mode", "light")

  return response
