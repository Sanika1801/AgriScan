import json

from django.db.models import F
from django.db.models.aggregates import Sum
from django.db.models.fields import DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from analytics.utils import send_sms
from .forms import ProductForm
from .models import Product, Category, CartItem, Order, OrderItem
from decimal import Decimal

def store(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    return render(request, 'marketplace/store.html', {'products': products, 'categories': categories})

@login_required
def add_to_cart(request, product_id):
    if request.user.role != 'farmer':
        return redirect('store')
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"Added {product.name} to cart!")
    return redirect('view_cart')

@login_required
def view_cart(request):
    if request.user.role != 'farmer':
        return redirect('store')
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'marketplace/cart.html', {'cart_items': cart_items, 'total': total})

# ==========================================
# NEW: STEP 1 - Show Payment Page
# ==========================================
@login_required
def checkout(request):
    if request.user.role != 'farmer':
        return redirect('store')
        
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('store')

    total = sum(item.total_price() for item in cart_items)
    
    # We ONLY render the payment page. We don't create the order yet.
    return render(request, 'marketplace/checkout.html', {
        'cart_items': cart_items, 
        'total': total
    })

# ==========================================
# NEW: STEP 2 - Process Payment & Create Order
# ==========================================
@login_required
def process_payment(request):
    if request.method != 'POST':
        return redirect('checkout')
        
    if request.user.role != 'farmer':
        return redirect('store')
        
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect('store')

    total = sum(item.total_price() for item in cart_items)
    
    # 1. Create the Order
    order = Order.objects.create(farmer=request.user, total_amount=total)
    
    # 2. Move Cart items to Order Items & Reduce Stock
    for item in cart_items:
        OrderItem.objects.create(
            order=order, 
            product=item.product, 
            quantity=item.quantity, 
            price=item.product.price
        )
        item.product.stock -= item.quantity
        item.product.save()
        
    # 3. Clear the Cart
    cart_items.delete()
    
    # 4. Send SMS Notifications
    if request.user.phone:
        send_sms(request.user.phone, f"AgriScan: Your payment of ₹{total} for Order #{order.id} was successful. Thank you!")
        
    sellers = set(item.product.seller for item in order.items.all())
    for seller in sellers:
        if seller.phone:
            send_sms(seller.phone, f"AgriScan Seller Alert: You have a new order (#{order.id}). Please check your dashboard.")
            
    # 5. Redirect to Success Page
    return render(request, 'marketplace/success.html', {'order': order})

@login_required
def seller_dashboard(request):
    if request.user.role != 'seller':
        return redirect('home')
        
    products = Product.objects.filter(seller=request.user)
    order_items = OrderItem.objects.filter(product__seller=request.user).order_by('-order__created_at')
    
    # 1. Calculate Total Revenue
    revenue_data = order_items.aggregate(
        total_revenue=Coalesce(Sum(F('quantity') * F('price'), output_field=DecimalField()), Decimal('0.00'))
    )
    total_revenue = revenue_data['total_revenue']

    # 2. Find Top Selling Products (for Chart.js)
    top_products = order_items.values('product__name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5] # Top 5 items

    chart_labels = [item['product__name'] for item in top_products]
    chart_data = [item['total_sold'] for item in top_products]

    # 3. Find Low Stock Alerts
    low_stock_products = products.filter(stock__lt=10)

    context = {
        'products': products,
        'order_items': order_items,
        'total_revenue': total_revenue,
        'low_stock_products': low_stock_products,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'marketplace/seller_dashboard.html', context)
    if request.user.role != 'seller':
        return redirect('home')
    products = Product.objects.filter(seller=request.user)
    order_items = OrderItem.objects.filter(product__seller=request.user).order_by('-order__created_at')
    return render(request, 'marketplace/seller_dashboard.html', {'products': products, 'order_items': order_items})

@login_required
def add_product(request):
    if request.user.role != 'seller':
        return redirect('home')
        
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user 
            product.save()
            messages.success(request, "✅ Product added successfully!")
            return redirect('seller_dashboard')
    else:
        form = ProductForm()
        
    return render(request, 'marketplace/add_product.html', {'form': form})