from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Person(models.Model):
    class GenderChoices(models.TextChoices):
        Male = "Male" , "Male"
        Female = "Female" , "Female"
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField()
    gender = models.CharField(max_length=8,choices= GenderChoices.choices)
    
    def __str__(self):
        return self.user.username


class PersonData(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE , related_name="Person")
    height = models.FloatField()
    weight = models.FloatField()
    goal = models.TextField()
    chronic_diseases = models.CharField(max_length=150 , null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"data for {self.person.user.username}"
    
class Specialist(models.Model):
    class GenderChoices(models.TextChoices):
        Male = "Male" , "Male"
        Famele = "Female" , "Female"

    class SpecialtyChoices(models.TextChoices):
        WEIGHT_LOSS = 'weight_loss', 'Weight Loss'
        WEIGHT_GAIN = 'weight_gain', 'Weight Gain'
        DIABETES = 'diabetes', 'Diabetes Nutrition'
        HYPERTENSION = 'hypertension', 'Hypertension Nutrition'
        CHOLESTEROL = 'cholesterol', 'Cholesterol Management Nutrition'
        WOMEN_HEALTH = 'women_health', 'Women Health'
        CHILDREN = 'children', 'Children Nutrition'
        SENIORS = 'seniors', 'Senior Nutrition'
        VEGAN = 'vegan', 'Vegan / Vegetarian'
        DIGESTIVE = 'digestive', 'Digestive Health Nutrition'
        IMMUNE = 'immune', 'Immune Support Nutrition'
        EATING_DISORDERS = 'eating_disorders', 'Eating Disorders Nutrition'
        GENERAL_HEALTH = 'general_health', 'General Health'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=8,choices= GenderChoices.choices)
    birth_date = models.DateField()
    specialization_certificate = models.FileField(upload_to='certificates/')
    specialty = models.CharField(max_length=30, choices=SpecialtyChoices.choices)
    image = models.ImageField(upload_to='images/', default='images/default_profile.jpg')
    
    def __str__(self):
        return self.user.username

class Certificate(models.Model):
    specialist = models.ForeignKey(Specialist ,on_delete=models.CASCADE , related_name="Certificates")
    name = models.CharField(max_length=255,null=True)
    image = models.FileField(upload_to='certificates/',null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return f"{self.name} - {self.specialist.user.username}"

class Director(models.Model):
    class GenderChoices(models.TextChoices):
        Male = "Male" , "Male"
        Famele = "Female" , "Female"
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=8,choices= GenderChoices.choices , null=True)
    birth_date = models.DateField(null=True)


    def __str__(self):
        return self.user.username

