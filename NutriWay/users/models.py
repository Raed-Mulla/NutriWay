from django.db import models
from accounts.models import Person
from specialists.models import Generalplan
# Create your models here.

class Subscription(models.Model):

    class StatusChoices(models.TextChoices):
        ACTIVE = 'active', 'Active'
        EXPIRED = 'expired', 'Expired'
        CANCELLED = 'cancelled', 'Cancelled'
    
    class DurationChoices(models.TextChoices):
        ONE_MONTH = '1_month', '1 Month'
        THREE_MONTHS = '3_months', '3 Months'
        SIX_MONTHS = '6_months', '6 Months'
        YEAR = '12_months', '12 Months'

    person = models.ForeignKey(Person,on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey("specialists.SubscriptionPlan",on_delete=models.CASCADE)
    subscriber_plan = models.ForeignKey("specialists.SubscriberPlan",on_delete=models.CASCADE,null=True,blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.CharField(max_length=20, choices=DurationChoices.choices,default=DurationChoices.ONE_MONTH)
    status = models.CharField(max_length=15 , choices=StatusChoices.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.person.user.username} - {self.subscription_plan.name}"


class ProgressReport(models.Model):
    subscription = models.ForeignKey(Subscription,on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.FloatField()
    note = models.TextField()
    specialist_comment = models.TextField(blank=True)

class GeneralPlanPurchase(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    general_plan = models.ForeignKey(Generalplan, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.person.user.username} bought {self.general_plan.name}"
