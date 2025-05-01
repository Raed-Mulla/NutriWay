from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from accounts.models import Person , Specialist
from .models import Review
from .forms import ReviewForm
from django.contrib import messages
from users.models import Subscription
from specialists.models import Specialist , Generalplan , SubscriptionPlan
from django.db.models import Avg , Max
from datetime import date

def add_review(request:HttpRequest , specialist_id):
  if not request.user.is_authenticated:
    messages.error(request, "You must be logged in to submit a review.", "alert-danger")
    return redirect("accounts:login_view")
    
  if hasattr(request.user, 'specialist') or hasattr(request.user, 'director') or request.user.is_staff:
    messages.error(request, "You are not authorized to submit reviews.", "alert-danger")
    return redirect("core:home_view")
  try:
    specialist = Specialist.objects.get(id=specialist_id)
    person = Person.objects.get(user=request.user)
  except (Specialist.DoesNotExist, Person.DoesNotExist):
    messages.error(request, "Specialist or user profile not found.", "alert-danger")
    return redirect("core:home_view")
  
  subscriptions = Subscription.objects.filter(person=person, subscription_plan__specialist=specialist)
  if not subscriptions.exists():
    messages.error(request, "You must have subscribed to this specialist before to leave a review.", "alert-danger")
    return redirect("core:home_view")
  
  latest_subscription = subscriptions.latest('end_date') 
  remaining_days = (latest_subscription.end_date - date.today()).days
  if remaining_days > 10:
    messages.error(request, f"You can only review in the last 10 days of your subscription. ({remaining_days} days left)", "alert-danger")
    return redirect("core:home_view")


  if Review.objects.filter(person=person, specialist=specialist).exists():
    messages.warning(request, "You have already submitted a review.", "alert-success")
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

  return render(request,'core/add_review.html' , {'form' : form , 'specialist' : specialist, 'ratingChoices':Review.RatingCohices.choices})


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

def calorie_calculator(request:HttpRequest):
  result = None

  if request.method == "POST":
    gender = request.POST.get('gender')
    age = int(request.POST.get('age'))
    weight = float(request.POST.get('weight'))
    height = float(request.POST.get('height'))
    activity = request.POST.get('activity')

    if gender == "male":
      bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    elif gender == "female":
      bmr = (10 * weight) + (6.25 * height) - (5  * age) - 161
    else:
      bmr = 0

    activity_factors = {
      "sedentary": 1.2,
      "light": 1.375,
      "moderate": 1.55,
      "active": 1.725
    }
    daily_calories = bmr * activity_factors.get(activity, 1.2)
    result = round(daily_calories)
  
    return render(request, "core/calorie_calculator.html", {"result": result})
  return render(request, "core/calorie_calculator.html")
