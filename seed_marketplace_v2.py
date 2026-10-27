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
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return ContentFile(response.content)
    except Exception as e:
        print(f"Failed to download image: {e}")
    return None

def seed_data():
    print("🌱 Re-seeding Marketplace Data with Real Images...")

    # 1. Ensure Seller Exists
    seller_user, _ = User.objects.get_or_create(
        username='agri_store',
        defaults={'role': 'seller', 'email': 'store@agriscan.com', 'phone': '9876543210'}
    )
    if not hasattr(seller_user, 'seller_profile'):
        SellerProfile.objects.create(user=seller_user, store_name="AgriStore Official")

    # 2. Clear old products (optional, but ensures a clean slate)
    Product.objects.all().delete()
    print("🗑️ Cleared old products.")

    # 3. Categories
    categories = ["Fertilizers", "Pesticides", "Seeds", "Farming Tools", "Irrigation"]
    cat_objs = {}
    for cat in categories:
        c, _ = Category.objects.get_or_create(name=cat)
        cat_objs[cat] = c

    # 4. New Product Data with DIRECT, reliable image links
    products_data = [
        {
            "name": "Organic Vermicompost Fertilizer",
            "category": "Fertilizers",
            "price": 350.00,
            "stock": 50,
            "desc": "100% organic vermicompost to boost soil fertility.",
            "img": "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?w=600&q=80"
        },
        {
            "name": "NPK 19:19:19 Water Soluble",
            "category": "Fertilizers",
            "price": 450.00,
            "stock": 120,
            "desc": "Premium water-soluble fertilizer for all crops.",
            "img": "https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?w=600&q=80"
        },
        {
            "name": "Neem Oil Bio-Pesticide",
            "category": "Pesticides",
            "price": 299.00,
            "stock": 80,
            "desc": "Natural neem extract to control pests safely.",
            "img": "https://images.unsplash.com/photo-1629851602598-214129f9d127?w=600&q=80"
        },
        {
            "name": "Chlorothalonil Fungicide",
            "category": "Pesticides",
            "price": 550.00,
            "stock": 40,
            "desc": "Effective fungicide for Late Blight and Scab.",
            "img": "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=600&q=80"
        },
        {
            "name": "Hybrid Tomato Seeds (100g)",
            "category": "Seeds",
            "price": 180.00,
            "stock": 200,
            "desc": "High-yield, disease-resistant tomato seeds.",
            "img": "https://images.unsplash.com/photo-1592841200221-a6898f307baa?w=600&q=80"
        },
        {
            "name": "Premium Wheat Seeds (5kg)",
            "category": "Seeds",
            "price": 850.00,
            "stock": 60,
            "desc": "Certified wheat seeds with excellent germination.",
            "img": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&q=80"
        },
        {
            "name": "Heavy Duty Steel Spade",
            "category": "Farming Tools",
            "price": 650.00,
            "stock": 30,
            "desc": "Durable steel spade for digging and soil prep.",
            "img": "https://images.unsplash.com/photo-1589923188900-85dae523342b?w=600&q=80"
        },
        {
            "name": "Battery Knapsack Sprayer",
            "category": "Farming Tools",
            "price": 1499.00,
            "stock": 15,
            "desc": "16-liter capacity sprayer for easy application.",
            "img": "https://images.unsplash.com/photo-1599839619722-39751411ea63?w=600&q=80"
        },
        {
            "name": "Drip Irrigation Kit (100m)",
            "category": "Irrigation",
            "price": 2200.00,
            "stock": 25,
            "desc": "Complete drip system to save water and boost yield.",
            "img": "https://images.unsplash.com/photo-1563514227147-6d2ff665a6a0?w=600&q=80"
        },
        {
            "name": "Rotary Lawn Sprinkler",
            "category": "Irrigation",
            "price": 450.00,
            "stock": 45,
            "desc": "Adjustable rotary sprinkler covering up to 1000 sq ft.",
            "img": "https://images.unsplash.com/photo-1589923188900-85dae523342b?w=600&q=80"
        }
    ]

    # 5. Create Products
    for p_data in products_data:
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

    print("\n🎉 Marketplace re-seeded with images!")

if __name__ == '__main__':
    seed_data()