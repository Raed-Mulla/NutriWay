from django.db import models

# Create your models here.
class ContactUs(models.Model):

    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        default= "Pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.status}"