from django.contrib import admin
from .models import Disease, Crop, CropCycle, PredictionLog

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'predicted_disease', 'confidence', 'date_uploaded')

admin.site.register(Crop)
admin.site.register(CropCycle)