from django.contrib import admin
from .models import SubscriptionPlan, Generalplan, SubscriberPlan, SubscriberMeal, MealCheck

# Register your models here.

class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialist', 'plan_type', 'duration', 'price')

class GeneralPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialist', 'price')

class SubscriberPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialist')

class SubscriberMealAdmin(admin.ModelAdmin):
    list_display = ('subscriber_plan', 'day_number', 'meal_type', 'meal_calorie')

class MealCheckAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'subscriber_meal', 'date', 'is_checked')


# تسجيلهم كلهم
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(Generalplan, GeneralPlanAdmin)
admin.site.register(SubscriberPlan, SubscriberPlanAdmin)
admin.site.register(SubscriberMeal, SubscriberMealAdmin)
admin.site.register(MealCheck, MealCheckAdmin)
