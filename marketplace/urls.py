from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'), 
    path('checkout/', views.checkout, name='checkout'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/add/', views.add_product, name='add_product'),
]