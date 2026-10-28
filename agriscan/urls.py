from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from accounts.views import register
from detector.views import custom_logout
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from accounts.models import FarmerProfile, AgronomistProfile
from detector.models import Disease
from marketplace.models import Category, Product

def setup_live_db(request):
    User = get_user_model()
    
    # 1. Create Admin
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'Admin@123')
    
    # 2. Create Farmer
    farmer, _ = User.objects.get_or_create(username='farmer_raj', defaults={'role': 'farmer'})
    farmer.set_password('pass12345')
    farmer.save()
    FarmerProfile.objects.get_or_create(user=farmer)

    # 3. Create 5 Experts
    experts = [
        {"username": "dr_smith", "spec": "Plant Pathology & Fungi", "exp": 12, "fee": 499.00},
        {"username": "dr_patel", "spec": "Horticulture & Vegetables", "exp": 8, "fee": 399.00},
        {"username": "dr_sharma", "spec": "Cereals & Wheat Specialist", "exp": 15, "fee": 599.00},
        {"username": "dr_reddy", "spec": "Soil Science & Fertilizers", "exp": 10, "fee": 450.00},
        {"username": "dr_singh", "spec": "Integrated Pest Management", "exp": 7, "fee": 350.00}
    ]
    for e in experts:
        u, _ = User.objects.get_or_create(username=e["username"], defaults={'role': 'agronomist'})
        u.set_password('pass12345')
        u.save()
        AgronomistProfile.objects.get_or_create(user=u, defaults={'specialization': e["spec"], 'experience_years': e["exp"], 'consultation_fee': e["fee"]})

    # 4. Create Diseases (This fixes the "Information not available" issue!)
    diseases = [
        ("Apple Scab", "A fungal disease causing olive-green spots.", "Apply fungicides.", "Prune trees."),
        ("Apple Healthy", "The plant is healthy.", "No treatment needed.", "Keep monitoring."),
        ("Tomato Late Blight", "A devastating fungal disease.", "Apply copper fungicides.", "Ensure air circulation."),
        ("Tomato Healthy", "The plant is healthy.", "No treatment needed.", "Keep monitoring."),
        ("Potato Early Blight", "Causes brown spots on leaves.", "Use mancozeb.", "Practice crop rotation."),
    ]
    for name, desc, treat, prev in diseases:
        Disease.objects.get_or_create(name=name, defaults={'description': desc, 'treatment': treat, 'prevention': prev, 'dosage_instructions': 'Follow label.', 'safety_advisory': 'Wear PPE.'})

    # 5. Create Marketplace Categories & Product
    cat, _ = Category.objects.get_or_create(name="Pesticides")
    seller, _ = User.objects.get_or_create(username='seller1', defaults={'role': 'seller'})
    seller.set_password('pass12345')
    seller.save()
    
    Product.objects.get_or_create(
        name="Organic Fungicide", seller=seller, category=cat, price=499.00, stock=50,
        defaults={'description': 'Cures most fungal diseases.'}
    )
    
    return HttpResponse("🎉 Live Database Setup Complete! You can now log in. <br><br><b>Admin:</b> admin / Admin@123<br><b>Farmer:</b> farmer_raj / pass12345<br><b>Expert:</b> dr_smith / pass12345")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('detector.urls')),
    path('marketplace/', include('marketplace.urls')), 
    path('community/', include('community.urls')),
    path('weather/', include('analytics.urls')),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('register/', register, name='register'),
    path('logout/', custom_logout, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add this block to serve media files in production
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)