from django.db import models
from accounts.models import Specialist

# Create your models here.
class SubscriptionPlan(models.Model):
    class PlanType(models.TextChoices):
        CLINICAL = 'clinical', 'Clinical Nutrition'
        WEIGHT_MANAGEMENT = 'weight', 'Weight Management'
        CHILDREN = 'children', 'Pediatric Nutrition'
        WOMEN = 'women', 'Womens Nutrition'
        CHRONIC = 'chronic', 'Chronic Conditions'
        VEGAN = 'vegan', 'Vegan/Vegetarian Nutrition'
        SENIORS = 'seniors', 'Geriatric Nutrition'
        DISORDERS = 'disorders', 'Eating Disorders'
        PREVENTIVE = 'preventive', 'Preventive Nutrition'

    class DurationChoices(models.TextChoices):
        ONE_MONTH = '1_month', '1 Month'
        THREE_MONTHS = '3_months', '3 Months'
        SIX_MONTHS = '6_months', '6 Months'
        YEAR = '12_months', '12 Months'
    
    specialist = models.ForeignKey(Specialist,on_delete=models.CASCADE, related_name="subscription_plans")
    name = models.CharField(max_length=128)
    description  = models.TextField()
    plan_type = models.CharField(max_length=30, choices=PlanType.choices)
    duration = models.CharField(max_length=20, choices=DurationChoices.choices,null=True , blank=True)
    price = models.FloatField()
    image = models.ImageField(upload_to='images/plans/')
    
    def __str__(self):
        return f"{self.name} - {self.specialist.user.username}"

class Generalplan(models.Model):
    specialist = models.ForeignKey(Specialist,on_delete=models.CASCADE, related_name="general_plans")
    name = models.CharField(max_length=128)
    description  = models.TextField()
    price = models.FloatField()
    plan_file = models.FileField(upload_to='general_plans/')

    def __str__(self):
        return f"General Plan: {self.name} ({self.specialist.user.username})"

class SubscriberPlan(models.Model):
    specialist = models.ForeignKey(Specialist,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return f"{self.name} - {self.specialist.user.username}"
    

class SubscriberMeal(models.Model):
    
    class MealTypeChoices(models.TextChoices):
        BREAKFAST = 'breakfast', 'Breakfast'
        LUNCH = 'lunch', 'Lunch'
        DINNER = 'dinner', 'Dinner'
        SNACK = 'snack', 'Snack'

    subscriber_plan = models.ForeignKey(SubscriberPlan,on_delete=models.CASCADE)
    day_number = models.IntegerField()
    meal_type = models.CharField(max_length=10,choices=MealTypeChoices.choices)
    description = models.TextField()
    meal_calorie = models.FloatField()

    def __str__(self):
        return f"{self.subscriber_plan.name} - Day {self.day_number} - {self.meal_type}"
    

class MealCheck(models.Model):
    subscription = models.ForeignKey("users.Subscription",on_delete=models.CASCADE)
    subscriber_meal = models.ForeignKey (SubscriberMeal,on_delete=models.CASCADE)
    date = models.DateField()
    is_checked = models.BooleanField(default=False)

    def __str__(self):
        return f"Check for {self.subscription.person.user.username} on {self.date} - {self.is_checked}"