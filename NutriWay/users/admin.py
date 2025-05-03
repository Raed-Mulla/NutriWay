from django.contrib import admin
from .models import Subscription, ProgressReport , GeneralPlanPurchase

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id','person', 'subscription_plan', 'subscriber_plan', 'start_date', 'end_date', 'duration', 'status')
    list_filter = ('status', 'duration', 'start_date', 'end_date')
    search_fields = ('person__user__username', 'subscription_plan__name')
    list_editable = ['end_date', 'status']
class ProgressReportAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'date', 'weight', 'specialist_comment')
    list_filter = ('date',)
    search_fields = ('subscription__person__user__username',)

class GeneralPlanPurchaseAdmin(admin.ModelAdmin):
    list_display =  ('person','general_plan','purchase_date')

admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(ProgressReport, ProgressReportAdmin)
admin.site.register(GeneralPlanPurchase, GeneralPlanPurchaseAdmin)
