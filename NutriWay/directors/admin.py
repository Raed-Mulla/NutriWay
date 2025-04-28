from django.contrib import admin
from .models import SpecialistRequest
# Register your models here.
class SpecialistRequestAdmin(admin.ModelAdmin):
    list_display = ['id','specialist','status','director']
    list_filter = ['status']
    list_editable = ['status', 'director']

admin.site.register(SpecialistRequest, SpecialistRequestAdmin)