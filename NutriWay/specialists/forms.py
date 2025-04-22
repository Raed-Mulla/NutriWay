from django import forms
from .models import SubscriptionPlan , Generalplan

class SubscriptionPlanForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        exclude = ['specialist']

class GeneralPlanForm(forms.ModelForm):
    class Meta:
        model = Generalplan
        exclude = ['specialist']