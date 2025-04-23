from django.contrib import admin
from .models import SpecialistRequest
# Register your models here.
class SpecialistRequestAdmin(admin.ModelAdmin):
    list_display = ['id','specialist','status','director']
    list_filter = ['status']

admin.site.register(SpecialistRequest, SpecialistRequestAdmin)