from django.contrib import admin
from .models import SubscriptionPlan, Generalplan

# Register your models here.

class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialist', 'plan_type', 'duration', 'price')



class GeneralPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialist', 'price')

admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(Generalplan, GeneralPlanAdmin)