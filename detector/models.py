from django.db import models
from django.conf import settings

class Disease(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    treatment = models.TextField()
    prevention = models.TextField()
    # NEW FIELDS:
    dosage_instructions = models.TextField(blank=True, null=True, help_text="Chemical application guidelines")
    safety_advisory = models.TextField(blank=True, null=True, help_text="Protection for ecosystem")

    def __str__(self):
        return self.name

class Crop(models.Model):
    name = models.CharField(max_length=100)
    season = models.CharField(max_length=50)
    def __str__(self): return self.name

class CropCycle(models.Model):
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'farmer'})
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    sowing_date = models.DateField()
    is_active = models.BooleanField(default=True)

class PredictionLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    crop_cycle = models.ForeignKey(CropCycle, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='uploads/')
    predicted_disease = models.CharField(max_length=100)
    confidence = models.FloatField()
    severity = models.PositiveIntegerField(default=0, help_text="Percentage of leaf affected")
    date_uploaded = models.DateTimeField(auto_now_add=True)
    
    REVIEW_STATUS = [
        ('pending', 'Pending Review'),
        ('verified', 'Verified by Expert')
    ]
    review_status = models.CharField(max_length=20, choices=REVIEW_STATUS, default='pending')
    expert_diagnosis = models.CharField(max_length=200, blank=True, null=True)
    organic_cure = models.TextField(blank=True, null=True)
    chemical_cure = models.TextField(blank=True, null=True)
    prevention_practice = models.TextField(blank=True, null=True)
    
    def __str__(self): return f"{self.user.username} - {self.predicted_disease}"