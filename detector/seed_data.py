import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriscan.settings')
import django
django.setup()

from detector.models import Disease

diseases = [
    {
        "name": "Apple Apple Scab", # Notice the space, matching the cleaned string
        "description": "A fungal disease that causes olive-green to black velvety spots on leaves.",
        "treatment": "Apply fungicides during bud break. Remove fallen leaves.",
        "prevention": "Plant resistant varieties and prune trees to improve airflow."
    },
    {
        "name": "Tomato Late Blight",
        "description": "A devastating fungal disease causing dark, water-soaked spots.",
        "treatment": "Apply copper-based fungicides immediately. Remove infected plants.",
        "prevention": "Ensure proper air circulation and avoid overhead watering."
    },
    {
        "name": "Potato Early Blight",
        "description": "Causes brown, concentric spots on older leaves, reducing yield.",
        "treatment": "Use fungicides containing mancozeb. Remove affected foliage.",
        "prevention": "Practice crop rotation and maintain adequate nitrogen."
    },
    {
        "name": "Corn Common Rust",
        "description": "Small, reddish-brown pustules on leaves.",
        "treatment": "Usually not fatal. Use resistant hybrids if severe.",
        "prevention": "Plant early in the season and use resistant varieties."
    }
]

for data in diseases:
    Disease.objects.update_or_create(name=data["name"], defaults=data)

print("✅ Disease database seeded successfully with clean names!")