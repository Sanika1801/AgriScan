from django.contrib import admin
from .models import Category, Product, Order, OrderItem, CartItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'category', 'price', 'stock')
    list_filter = ('category', 'seller')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'farmer', 'total_amount', 'status', 'created_at')
    list_filter = ('status',)

admin.site.register(Category)
admin.site.register(OrderItem)
admin.site.register(CartItem)