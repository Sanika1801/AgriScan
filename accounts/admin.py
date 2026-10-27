from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FarmerProfile, AgronomistProfile, SellerProfile # <-- Add SellerProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (('Custom Profile', {'fields': ('role', 'phone')}),)

admin.site.register(FarmerProfile)
admin.site.register(AgronomistProfile)
admin.site.register(SellerProfile) 