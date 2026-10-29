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
    try:
        User = get_user_model()
        
        # 1. FORCE CREATE/UPDATE ADMIN
        admin, _ = User.objects.get_or_create(username='admin')
        admin.set_password('Admin@123')
        admin.is_superuser = True
        admin.is_staff = True
        admin.role = 'admin'
        admin.save()
        
        # 2. FORCE CREATE/UPDATE FARMER
        farmer, _ = User.objects.get_or_create(username='farmer_raj')
        farmer.set_password('pass12345')
        farmer.role = 'farmer'
        farmer.save()
        FarmerProfile.objects.get_or_create(user=farmer)
        
        # 3. FORCE CREATE/UPDATE SELLER
        seller, _ = User.objects.get_or_create(username='seller1')
        seller.set_password('pass12345')
        seller.role = 'seller'
        seller.save()

        # 4. FORCE CREATE/UPDATE EXPERTS
        experts = [
            {"username": "dr_smith", "spec": "Plant Pathology & Fungi", "exp": 12, "fee": 499.00},
            {"username": "dr_patel", "spec": "Horticulture & Vegetables", "exp": 8, "fee": 399.00},
            {"username": "dr_sharma", "spec": "Cereals & Wheat Specialist", "exp": 15, "fee": 599.00},
            {"username": "dr_reddy", "spec": "Soil Science & Fertilizers", "exp": 10, "fee": 450.00},
            {"username": "dr_singh", "spec": "Integrated Pest Management", "exp": 7, "fee": 350.00}
        ]
        for e in experts:
            u, _ = User.objects.get_or_create(username=e["username"])
            u.set_password('pass12345')
            u.role = 'agronomist'
            u.save()
            AgronomistProfile.objects.get_or_create(user=u, defaults={'specialization': e["spec"], 'experience_years': e["exp"], 'consultation_fee': e["fee"]})

        # 5. CREATE DISEASES
        diseases = [
            ("Apple Scab", "A fungal disease causing olive-green spots.", "Apply fungicides.", "Prune trees."),
            ("Apple Healthy", "The plant is healthy.", "No treatment needed.", "Keep monitoring."),
            ("Tomato Late Blight", "A devastating fungal disease.", "Apply copper fungicides.", "Ensure air circulation."),
            ("Tomato Healthy", "The plant is healthy.", "No treatment needed.", "Keep monitoring."),
        ]
        for name, desc, treat, prev in diseases:
            Disease.objects.get_or_create(name=name, defaults={'description': desc, 'treatment': treat, 'prevention': prev, 'dosage_instructions': 'Follow label.', 'safety_advisory': 'Wear PPE.'})

        # 6. CREATE CATEGORIES
        cat_fert, _ = Category.objects.get_or_create(name="Fertilizers")
        cat_pest, _ = Category.objects.get_or_create(name="Pesticides")
        cat_seeds, _ = Category.objects.get_or_create(name="Seeds")
        cat_tools, _ = Category.objects.get_or_create(name="Farming Tools")

        # 7. CREATE 8 PRODUCTS
        products_data = [
            ("Organic Vermicompost", cat_fert, 350.00, 50, "100% organic vermicompost."),
            ("NPK 19:19:19 Water Soluble", cat_fert, 450.00, 120, "Premium water-soluble fertilizer."),
            ("Neem Oil Bio-Pesticide", cat_pest, 299.00, 80, "Natural neem extract."),
            ("Chlorothalonil Fungicide", cat_pest, 550.00, 40, "Effective for Late Blight."),
            ("Hybrid Tomato Seeds (100g)", cat_seeds, 180.00, 200, "High-yield seeds."),
            ("Premium Wheat Seeds (5kg)", cat_seeds, 850.00, 60, "Certified wheat seeds."),
            ("Heavy Duty Steel Spade", cat_tools, 650.00, 30, "Durable steel spade."),
            ("Battery Knapsack Sprayer", cat_tools, 1499.00, 15, "16-liter sprayer.")
        ]

        for name, cat, price, stock, desc in products_data:
            Product.objects.get_or_create(
                name=name, 
                defaults={'seller': seller, 'category': cat, 'price': price, 'stock': stock, 'description': desc}
            )
        
        return HttpResponse("🎉 SUCCESS! The database is reset and populated with 8 products.<br><br>Try logging in now with:<br><b>farmer_raj</b> / pass12345")
        
    except Exception as e:
        return HttpResponse(f"❌ ERROR: The script failed. Reason: {str(e)}")

urlpatterns = [
    path('setup-db/', setup_live_db),
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
