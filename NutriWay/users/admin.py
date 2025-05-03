from django.contrib import admin
from .models import Subscription, ProgressReport

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id','person', 'subscription_plan', 'subscriber_plan', 'start_date', 'end_date', 'duration', 'status')
    list_filter = ('status', 'duration', 'start_date', 'end_date')
    search_fields = ('person__user__username', 'subscription_plan__name')
    list_editable = ['end_date', 'status']
class ProgressReportAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'date', 'weight', 'specialist_comment')
    list_filter = ('date',)
    search_fields = ('subscription__person__user__username',)

admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(ProgressReport, ProgressReportAdmin)
