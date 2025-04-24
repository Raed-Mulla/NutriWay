from django.db import models
from accounts.models import Specialist,Director
# Create your models here.
class SpecialistRequest(models.Model):

    class RequestStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    specialist = models.ForeignKey(Specialist , on_delete=models.CASCADE)
    director = models.ForeignKey(Director , on_delete=models.SET_NULL,blank=True,null=True)
    status = models.CharField(max_length=10 , choices=RequestStatus.choices , default=RequestStatus.PENDING)
    feedback = models.TextField(blank=True)

    def __str__(self):
        return f"Request by {self.specialist.user.username} - {self.status}"