from django.contrib import admin
from .models import Person, PersonData, Specialist, Certificate, Director

class PersonAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'gender')
    search_fields = ('user__username',)

class PersonDataAdmin(admin.ModelAdmin):
    list_display = ('person', 'height', 'weight', 'created_at')
    search_fields = ('person__user__username',)

class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'gender')
    list_filter = ('specialty', 'gender')
    search_fields = ('user__username',)

class CertificateAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialist', 'created_at')
    search_fields = ('name', 'specialist__user__username')

class DirectorAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)

# تسجيل الموديلات في لوحة التحكم
admin.site.register(Person, PersonAdmin)
admin.site.register(PersonData, PersonDataAdmin)
admin.site.register(Specialist, SpecialistAdmin)
admin.site.register(Certificate, CertificateAdmin)
admin.site.register(Director, DirectorAdmin)
