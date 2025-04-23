from django.db import models
from accounts.models import Person, Specialist
# Create your models here.
class Review(models.Model):
    class RatingCohices(models.IntegerChoices):
        one = 1 , "1"
        two = 2 , "2"
        three = 3 , "3"
        four = 4 , "4"
        five = 5 , "5"

    person = models.ForeignKey(Person,on_delete=models.CASCADE,related_name="reviews")
    specialist = models.ForeignKey(Specialist,on_delete=models.CASCADE,related_name="reviews")
    comment = models.TextField()
    rating = models.IntegerField(choices=RatingCohices)

    def __str__(self):
        return f"{self.person.user.username} → {self.specialist.user.username}"