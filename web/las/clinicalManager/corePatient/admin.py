from django.contrib import admin
from corePatient.models import Patient


class PatientAdmin(admin.ModelAdmin):
    list_display = ['fiscalCode', 'firstName', 'lastName']

admin.site.register(Patient, PatientAdmin)

