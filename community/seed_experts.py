import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriscan.settings')
import django
django.setup()

from accounts.models import User, AgronomistProfile

# Create Expert User
expert_user, created = User.objects.get_or_create(
    username='dr_smith', 
    defaults={'role': 'agronomist', 'email': 'smith@agriscan.com'}
)
if created:
    expert_user.set_password('pass12345')
    expert_user.save()

# Create Expert Profile
AgronomistProfile.objects.get_or_create(
    user=expert_user,
    defaults={
        'specialization': 'Plant Pathology & Fungi',
        'experience_years': 12,
        'consultation_fee': 499.00
    }
)
print("✅ Agronomist 'dr_smith' created! (Password: pass12345)")