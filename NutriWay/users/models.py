from django.db import models
from accounts.models import Person
# Create your models here.

class Subscription(models.Model):

    class StatusChoices(models.TextChoices):
        ACTIVE = 'active', 'Active'
        EXPIRED = 'expired', 'Expired'
        CANCELLED = 'cancelled', 'Cancelled'

    person = models.ForeignKey(Person,on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey("specialists.SubscriptionPlan",on_delete=models.CASCADE)
    subscriber_plan = models.ForeignKey("specialists.SubscriberPlan",on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=15 , choices=StatusChoices.choices)

    def __str__(self):
        return f"{self.person.user.username} - {self.subscription_plan.name}"


class ProgressReport(models.Model):
    subscription = models.ForeignKey("specialists.SubscriptionPlan",on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.FloatField()
    note = models.TextField()
    specialist_comment = models.TextField(blank=True)