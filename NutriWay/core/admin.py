from django.contrib import admin
from.models import Review
# Register your models here.

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('person','specialist','comment','rating')


admin.site.register(Review, ReviewAdmin)
