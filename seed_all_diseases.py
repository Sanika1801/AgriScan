import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriscan.settings')
django.setup()

from detector.models import Disease

def clean_name(raw_name):
    if '___' in raw_name:
        crop, disease = raw_name.split('___', 1)
        disease = disease.replace('_', ' ').title()
        if disease.lower().startswith(crop.lower()):
            return disease
        return f"{crop.capitalize()} {disease}"
    return raw_name.replace('_', ' ').title()

def seed_all():
    with open('class_names.txt', 'r') as f:
        raw_names = [line.strip() for line in f.readlines()]

    count = 0
    for raw in raw_names:
        clean = clean_name(raw)
        
        if "Healthy" in clean:
            desc = "The plant appears completely healthy with no visible signs of disease."
            treat = "No treatment required. Continue regular watering and fertilization."
            prev = "Maintain current crop management practices to prevent future infections."
            dose = "N/A"
            safe = "N/A"
        else:
            desc = f"A disease affecting the plant. Symptoms typically include spots, discoloration, or wilting on the leaves."
            treat = f"Apply appropriate fungicides or bactericides targeted for {clean}. Remove severely infected leaves."
            prev = "Ensure proper air circulation, avoid overhead watering, and rotate crops."
            dose = "Mix 2ml of recommended fungicide per 1 liter of water. Spray evenly on affected areas."
            safe = "Wear protective gear. Avoid spraying near water bodies or during high winds to protect pollinators."

        # Create the disease in the database
        Disease.objects.update_or_create(
            name=clean,
            defaults={
                'description': desc,
                'treatment': treat,
                'prevention': prev,
                'dosage_instructions': dose,
                'safety_advisory': safe
            }
        )
        count += 1

    print(f"✅ Successfully seeded {count} diseases into the database!")

if __name__ == '__main__':
    seed_all()