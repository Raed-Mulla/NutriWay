from django import forms
from .models import SubscriptionPlan , Generalplan , SubscriberPlan,SubscriberMeal
from django.forms import modelformset_factory

class SubscriptionPlanForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        exclude = ['specialist']

class GeneralPlanForm(forms.ModelForm):
    class Meta:
        model = Generalplan
        exclude = ['specialist', 'created_at']

class SubscriberPlanForm(forms.ModelForm):
    class Meta:
        model = SubscriberPlan
        fields = ['name', 'description']

class SubscriberMealForm(forms.ModelForm):
    class Meta:
        model = SubscriberMeal
        fields = ['day_number', 'meal_type', 'description', 'meal_calorie']


SubscriberMealFormSet = modelformset_factory(
    SubscriberMeal,
    form=SubscriberMealForm,
    extra=1,
    can_delete=True
)