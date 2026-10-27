import os
import django
import requests
from django.core.files.base import ContentFile

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriscan.settings')
django.setup()

from accounts.models import User, SellerProfile
from marketplace.models import Category, Product

def download_image(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return ContentFile(response.content)
    except Exception as e:
        print(f"Failed to download image: {e}")
    return None

def seed_data():
    print("🌱 Seeding Marketplace Data...")

    # 1. Create a Seller
    seller_user, created = User.objects.get_or_create(
        username='agri_store',
        defaults={'role': 'seller', 'email': 'store@agriscan.com', 'phone': '9876543210'}
    )
    if created:
        seller_user.set_password('pass12345')
        seller_user.save()
        SellerProfile.objects.create(user=seller_user, store_name="AgriStore Official")
        print("✅ Created Seller: agri_store / pass12345")

    # 2. Create Categories
    categories = ["Fertilizers", "Pesticides", "Seeds", "Farming Tools", "Irrigation"]
    cat_objs = {}
    for cat in categories:
        c, _ = Category.objects.get_or_create(name=cat)
        cat_objs[cat] = c
    print("✅ Created 5 Categories")

    # 3. Product Data with High-Quality Unsplash Image URLs
    products_data = [
        {
            "name": "Organic Vermicompost Fertilizer",
            "category": "Fertilizers",
            "price": 350.00,
            "stock": 50,
            "desc": "100% organic vermicompost to boost soil fertility and plant growth.",
            "img": "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?q=80&w=600&auto=format&fit=crop"
        },
        {
            "name": "NPK 19:19:19 Water Soluble",
            "category": "Fertilizers",
            "price": 450.00,
            "stock": 120,
            "desc": "Premium water-soluble fertilizer suitable for all crops.",
            "img": "https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?q=80&w=600&auto=format&fit=crop"
        },
        {
            "name": "Neem Oil Bio-Pesticide",
            "category": "Pesticides",
            "price": 299.00,
            "stock": 80,
            "desc": "Natural neem extract to control pests without harming the environment.",
            "img": "https://images.unsplash.com/photo-1629851602598-214129f9d127?q=80&w=600&auto=format&fit=crop"
        },
        {
            "name": "Chlorothalonil 75% WP Fungicide",
            "category": "Pesticides",
            "price": 550.00,
            "stock": 40,
            "desc": "Effective fungicide for Late Blight and Scab diseases.",
            "img": "https://images.unsplash.com/photo-1574943320219-553eb213f72d?q=80&w=600&auto=format&fit=crop"
        },
        {
            "name": "Hybrid Tomato Seeds (100g)",
            "category": "Seeds",
            "price": 180.00,
            "stock": 200,
            "desc": "High-yield, disease-resistant tomato seeds.",
            "img": "https://images.unsplash.com/photo-1592841200221-a6898f307baa?q=80&w=600&auto=format&fit=crop"
        },
        {
            "name": "Premium Wheat Seeds (5kg)",
            "category": "Seeds",
            "price": 850.00,
            "stock": 60,
            "desc": "Certified wheat seeds with excellent germination rate.",
            "img": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?q=80&w=600&auto=format&fit=crop"
        },
        {
            "name": "Heavy Duty Steel Spade",
            "category": "Farming Tools",
            "price": 650.00,
            "stock": 30,
            "desc": "Durable steel spade for digging and soil preparation.",
            "img": "https://images.unsplash.com/photo-1416879598555-220b8db1f9ce?q=80&w=600&auto=format&fit=crop"
        },
        {
            "name": "Battery Operated Knapsack Sprayer",
            "category": "Farming Tools",
            "price": 1499.00,
            "stock": 15,
            "desc": "16-liter capacity sprayer for easy pesticide application.",
            "img": "https://images.unsplash.com/photo-1629851602598-214129f9d127?q=80&w=600&auto=format&fit=crop"
        },
        {
            "name": "Drip Irrigation Kit (100m)",
            "category": "Irrigation",
            "price": 2200.00,
            "stock": 25,
            "desc": "Complete drip irrigation system to save water and increase yield.",
            "img": "https://images.unsplash.com/photo-1563514227147-6d2ff665a6a0?q=80&w=600&auto=format&fit=crop"
        },
        {
            "name": "Rotary Lawn Sprinkler",
            "category": "Irrigation",
            "price": 450.00,
            "stock": 45,
            "desc": "Adjustable rotary sprinkler covering up to 1000 sq ft.",
            "img": "https://images.unsplash.com/photo-1589923188900-85dae523342b?q=80&w=600&auto=format&fit=crop"
        }
    ]

    # 4. Download Images and Create Products
    for p_data in products_data:
        if not Product.objects.filter(name=p_data["name"]).exists():
            print(f"Downloading image for {p_data['name']}...")
            image_file = download_image(p_data["img"])
            
            product = Product(
                seller=seller_user,
                category=cat_objs[p_data["category"]],
                name=p_data["name"],
                description=p_data["desc"],
                price=p_data["price"],
                stock=p_data["stock"]
            )
            
            if image_file:
                product.image.save(f"{p_data['name'].replace(' ', '_').lower()}.jpg", image_file, save=True)
            else:
                product.save()
            
            print(f"✅ Added: {p_data['name']}")
        else:
            print(f"⏭️ Skipping (already exists): {p_data['name']}")

    print("\n🎉 Marketplace Seeded Successfully!")

if __name__ == '__main__':
    seed_data()