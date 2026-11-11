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
        admin.set_password('pass12345')
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

                # 5. CREATE DISEASES (All 38 PlantVillage Classes)
        diseases = [
            ("Apple Scab", "A fungal disease causing olive-green spots.", "Apply fungicides.", "Prune trees."),
            ("Apple Black Rot", "A fungal disease causing frogeye leaf spots.", "Remove infected branches.", "Ensure proper pruning."),
            ("Cedar Apple Rust", "A fungal disease causing yellow-orange spots.", "Apply rust-specific fungicides.", "Remove nearby cedar trees."),
            ("Apple Healthy", "The plant is healthy.", "No treatment needed.", "Keep monitoring."),
            ("Blueberry Healthy", "The plant is healthy.", "No treatment needed.", "Keep monitoring."),
            ("Cherry Powdery Mildew", "A fungal disease causing white powdery growth.", "Apply sulfur-based fungicides.", "Improve air circulation."),
            ("Cherry Healthy", "The plant is healthy.", "No treatment needed.", "Keep monitoring."),
            ("Corn Cercospora Leaf Spot", "A fungal disease causing gray to brown lesions.", "Apply foliar fungicides.", "Rotate crops."),
            ("Corn Common Rust", "A fungal disease causing reddish-brown pustules.", "Apply fungicides early.", "Plant resistant hybrids."),
            ("Corn Northern Leaf Blight", "A fungal disease causing cigar-shaped lesions.", "Apply fungicides.", "Crop rotation."),
            ("Corn Healthy", "The plant is healthy.", "No treatment needed.", "Keep monitoring."),
            ("Grape Black Rot", "A fungal disease causing brown spots on leaves.", "Remove mummified berries.", "Apply fungicides."),
            ("Grape Esca", "A complex wood disease.", "No cure, remove infected vines.", "Prune properly."),
            ("Grape Leaf Blight", "A fungal disease causing brown spots.", "Apply copper fungicides.", "Ensure good drainage."),
            ("Grape Healthy", "The plant is healthy.", "No treatment needed.", "Keep monitoring."),
            ("Orange Haunglongbing", "Citrus greening disease spread by insects.", "Remove infected trees.", "Control psyllid insects."),
            ("Peach Bacterial Spot", "A bacterial disease causing dark spots.", "Apply copper sprays.", "Plant resistant varieties."),
            ("Peach Healthy", "The plant is healthy.", "No treatment needed.", "Keep monitoring."),
            ("Pepper Bell Bacterial Spot", "A bacterial disease causing water-soaked spots.", "Apply copper-based bactericides.", "Avoid overhead watering."),
            ("Pepper Bell Healthy", "The plant is healthy.", "No treatment needed.", "Keep monitoring."),
            ("Potato Early Blight", "A fungal disease causing dark concentric rings.", "Apply chlorothalonil.", "Crop rotation."),
            ("Potato Late Blight", "A devastating fungal disease causing dark lesions.", "Apply copper fungicides immediately.", "Destroy infected plants."),
            ("Potato Healthy", "The plant is healthy.", "No treatment needed.", "Keep monitoring."),
            ("Raspberry Healthy", "The plant is healthy.", "No treatment needed.", "Keep monitoring."),
            ("Soybean Healthy", "The plant is healthy.", "No treatment needed.", "Keep monitoring."),
            ("Squash Powdery Mildew", "A fungal disease causing white powdery spots.", "Apply neem oil or sulfur.", "Ensure good airflow."),
            ("Strawberry Leaf Scorch", "A fungal disease causing purple spots.", "Apply fungicides.", "Remove old leaves."),
            ("Strawberry Healthy", "The plant is healthy.", "No treatment needed.", "Keep monitoring."),
            ("Tomato Bacterial Spot", "A bacterial disease causing small dark spots.", "Apply copper sprays.", "Use disease-free seeds."),
            ("Tomato Early Blight", "A fungal disease causing target-like spots.", "Apply fungicides.", "Mulch around plants."),
            ("Tomato Late Blight", "A devastating fungal disease.", "Apply copper fungicides.", "Ensure air circulation."),
            ("Tomato Leaf Mold", "A fungal disease causing yellow spots.", "Improve ventilation.", "Reduce humidity."),
            ("Tomato Septoria Leaf Spot", "A fungal disease causing small circular spots.", "Apply fungicides.", "Remove lower leaves."),
            ("Tomato Spider Mites", "Pest causing stippling on leaves.", "Apply miticides.", "Increase humidity."),
            ("Tomato Target Spot", "A fungal disease causing concentric rings.", "Apply fungicides.", "Crop rotation."),
            ("Tomato Yellow Leaf Curl", "A viral disease spread by whiteflies.", "Control whiteflies.", "Use resistant varieties."),
            ("Tomato Mosaic Virus", "A viral disease causing mottling.", "No cure, destroy plants.", "Disinfect tools."),
            ("Tomato Healthy", "The plant is healthy.", "No treatment needed.", "Keep monitoring."),
        ]
        
        for name, desc, treat, prev in diseases:
            Disease.objects.get_or_create(
                name=name, 
                defaults={
                    'description': desc, 
                    'treatment': treat, 
                    'prevention': prev, 
                    'dosage_instructions': 'Apply as per manufacturer guidelines on the product label.', 
                    'safety_advisory': 'Avoid spraying during high winds or near water bodies to protect pollinators.'
                }
            )

        # 6. CREATE CATEGORIES
        cat_fert, _ = Category.objects.get_or_create(name="Fertilizers")
        cat_pest, _ = Category.objects.get_or_create(name="Pesticides")
        cat_seeds, _ = Category.objects.get_or_create(name="Seeds")
        cat_tools, _ = Category.objects.get_or_create(name="Farming Tools")
        
                # 7. CREATE FORUM POSTS & COMMENTS
        from community.models import ForumPost, ForumComment
        
        farmer_dev, _ = User.objects.get_or_create(username='farmer_dev', defaults={'role': 'farmer'})

        forum_data = [
            {
                "title": "White spots on my tomato leaves - is this Late Blight?",
                "content": "I noticed white powdery spots on the lower leaves of my tomato plants yesterday. It has been very humid here. I used the AI scanner and it said 'Tomato Late Blight' with 85% confidence. Does anyone know the best organic treatment for this?",
                "comments": [
                    (User.objects.get(username='dr_smith'), "Yes, that is Late Blight. You need to act fast. Remove the infected leaves immediately and spray a copper-based fungicide. Avoid watering the leaves directly."),
                    (farmer_dev, "I had the same issue last week. I used Neem oil and it helped slow it down."),
                ]
            },
            {
                "title": "Yellowing of wheat crop in Sector 4",
                "content": "My wheat crop is turning yellow from the tips of the leaves. The soil pH is around 6.5. Could this be a nitrogen deficiency or a disease?",
                "comments": [
                    (User.objects.get(username='dr_smith'), "Yellowing from the tips usually indicates a Nitrogen deficiency. Try applying a urea top-dressing."),
                ]
            }
        ]

        for p_data in forum_data:
            post, created = ForumPost.objects.get_or_create(
                title=p_data["title"],
                defaults={'author': farmer, 'content': p_data["content"]}
            )
            if created:
                for c_author, c_text in p_data["comments"]:
                    ForumComment.objects.create(post=post, author=c_author, content=c_text)

        # 8. CREATE 8 PRODUCTS
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
            
                    # 9. CREATE MARKET PRICES (for the Mandi Widget)
        from detector.models import MarketPrice
        from datetime import date, timedelta
        import random

        crops = ['Wheat', 'Tomato', 'Grapes', 'Potato']
        for crop in crops:
            base_price = random.randint(1500, 2500)
            # Create data for the last 7 days
            for i in range(7):
                d = date.today() - timedelta(days=i)
                # Add random daily variation
                price = base_price + random.randint(-150, 150) 
                MarketPrice.objects.get_or_create(crop_name=crop, date=d, defaults={'price_per_quintal': price})
        
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
