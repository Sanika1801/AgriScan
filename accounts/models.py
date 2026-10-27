from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('agronomist', 'Agronomist'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='farmer')
    phone = models.CharField(max_length=15, blank=True)

class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    location = models.CharField(max_length=100)
    farm_size_acres = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    soil_type = models.CharField(max_length=50, blank=True)

class AgronomistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agronomist_profile')
    specialization = models.CharField(max_length=100)
    experience_years = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    
class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    store_name = models.CharField(max_length=100)
    gst_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.store_name} ({self.user.username})"