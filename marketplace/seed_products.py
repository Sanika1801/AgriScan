import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriscan.settings')
import django
django.setup()

from marketplace.models import Category, Product
from accounts.models import User

# Create a Seller
seller, _ = User.objects.get_or_create(username='agri_seller', role='seller')

# Create Categories
fert, _ = Category.objects.get_or_create(name='Fertilizers')
pest, _ = Category.objects.get_or_create(name='Pesticides')
seeds, _ = Category.objects.get_or_create(name='Seeds')

# Create Products
products = [
    ("Organic NPK Fertilizer", 450.00, fert, "Boosts plant growth naturally."),
    ("Tomato Late Blight Fungicide", 299.00, pest, "Effective against late blight disease."),
    ("Apple Scab Treatment Spray", 550.00, pest, "Protects apple trees from scab."),
    ("Premium Wheat Seeds (1kg)", 120.00, seeds, "High yield, disease-resistant wheat seeds."),
    ("Neem Oil Concentrate", 199.00, pest, "Organic pesticide for all crops.")
]

for name, price, cat, desc in products:
    Product.objects.get_or_create(
        name=name, 
        defaults={'price': price, 'category': cat, 'seller': seller, 'description': desc, 'stock': 100}
    )

print("✅ Marketplace seeded successfully!")