import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriscan.settings')
django.setup()

from detector.models import Disease

diseases = [
    {
        "name": "Tomato___Late_blight",
        "description": "A fungal disease causing dark, water-soaked spots on leaves and stems, eventually killing the plant.",
        "treatment": "Apply copper-based fungicides or chlorothalonil. Remove infected leaves immediately.",
        "prevention": "Ensure proper air circulation, avoid overhead watering, and rotate crops."
    },
    {
        "name": "Potato___Early_blight",
        "description": "A common fungal infection causing brown, concentric spots on older leaves, reducing crop yield.",
        "treatment": "Use fungicides containing mancozeb or chlorothalonil. Remove affected foliage.",
        "prevention": "Maintain adequate nitrogen levels and practice crop rotation."
    },
    {
        "name": "Apple___Apple_scab",
        "description": "A fungal disease that causes olive-green to black velvety spots on leaves and scabby lesions on fruit.",
        "treatment": "Apply fungicides during bud break and early spring. Remove fallen leaves.",
        "prevention": "Plant resistant varieties and prune trees to improve airflow."
    },
    {
        "name": "Corn___Common_rust",
        "description": "Characterized by small, reddish-brown pustules on leaves that can reduce photosynthesis.",
        "treatment": "Fungicides are usually not necessary unless the infection is severe and early. Use resistant hybrids.",
        "prevention": "Plant early in the season and use resistant corn varieties."
    },
    {
        "name": "Healthy",
        "description": "The leaf is perfectly healthy with no signs of infection.",
        "treatment": "No treatment required!",
        "prevention": "Maintain current watering and nutrient schedules."
    }
]

for data in diseases:
    Disease.objects.get_or_create(
        name=data["name"],
        defaults={
            "description": data["description"],
            "treatment": data["treatment"],
            "prevention": data["prevention"]
        }
    )

print("✅ Disease database seeded successfully!")