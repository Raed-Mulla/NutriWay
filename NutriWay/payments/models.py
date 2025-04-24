from django.db import models
from django.db import models
from accounts.models import Person
from specialists.models import SubscriptionPlan, Specialist, Generalplan

class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        VISA = 'visa', 'Visa'
        MASTERCARD = 'mastercard', 'MasterCard'

    class StatusChoices(models.TextChoices):
        PAID = 'Paid', 'Paid'
        PENDING = 'Pending', 'Pending'
        FAILED = 'Failed', 'Failed'

    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='payments')
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='payments')
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    general_plan = models.ForeignKey(Generalplan, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.FloatField()
    paid_at = models.DateTimeField(auto_now_add=True)

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.VISA 
    )

    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.PAID
    )

    stripe_session_id = models.CharField(max_length=255, null=True, blank=True)

    def str(self):
        return f"{self.person.user.username} paid {self.amount} to {self.specialist.user.username} via {self.payment_method} ({self.status})"

