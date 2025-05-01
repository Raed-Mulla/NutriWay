from django.contrib import admin
from .models import Payment, SubscriptionPlan

# Register your models here.
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'person',
        'specialist',
        'subscription_plan',
        'get_plan_type',
        'get_duration_display',
        'general_plan',
        'amount',
        'status',
        'payment_method',
        'paid_at',
    )
    list_filter = ('status', 'payment_method', 'paid_at')
    search_fields = ('person__user__username', 'specialist__user__username')
    readonly_fields = ('paid_at',)

    @admin.display(description="Plan Type")  
    def get_plan_type(self, obj: Payment) -> str:
        if obj.subscription_plan:
            return obj.subscription_plan.get_plan_type_display()  # show label 
        return '—'
    
    def get_duration_display(self, obj):
        if obj.selected_duration:
            return dict(SubscriptionPlan.DurationChoices.choices).get(obj.selected_duration, 'Unknown')
    
    get_duration_display.short_description = "Duration"