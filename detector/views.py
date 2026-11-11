import os
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from .models import PredictionLog, Disease
from marketplace.models import Product
from django.contrib.auth import logout
from django.db.models import Count
from marketplace.models import Order
from community.models import ExpertConsultation, ForumPost
from django.contrib.auth import get_user_model
from django.http import FileResponse, JsonResponse
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from .gradcam import generate_gradcam
from analytics.utils import send_sms, get_disease_risk_alert
from .forms import CropCycleForm 
from .models import MarketPrice
from django.db.models import Avg

# Import the new Predictor
from .predictor import AgriPredictor

MODEL_PATH = os.path.join(settings.BASE_DIR, 'crop_disease_model.h5')
CLASS_NAMES_PATH = os.path.join(settings.BASE_DIR, 'class_names.txt')

try:
    with open(CLASS_NAMES_PATH, 'r') as f:
        CLASS_NAMES = [line.strip() for line in f.readlines()]
    AI_MODEL = AgriPredictor(MODEL_PATH, CLASS_NAMES)
except Exception as e:
    AI_MODEL = None
    print(f"⚠️ AI Model not loaded: {e}")

def upload_image(request):
    # 1. Role-based redirects for logged-in users
    if request.user.is_authenticated:
        if request.user.role == 'seller':
            return redirect('seller_dashboard')
        elif request.user.role == 'agronomist':
            return redirect('agronomist_dashboard')
        elif request.user.role == 'admin' or request.user.is_superuser:
            return redirect('admin_dashboard')

    # 2. Handle POST requests (Uploading an image)
    if request.method == 'POST' and request.FILES.get('leaf_image'):
        if not request.user.is_authenticated:
            return redirect('login') 
            
        uploaded_file = request.FILES['leaf_image']
        
        if AI_MODEL is None:
            return render(request, 'error.html', {'error': 'AI Model not loaded.'})
            
        # Save image
        log = PredictionLog.objects.create(
            user=request.user,
            image=uploaded_file, 
            predicted_disease="Processing...",
            confidence=0, 
            severity=0
        )
        
        file_path = log.image.path
        filename = os.path.basename(log.image.name)
        
        # AI Prediction (Top-3 + OOD)
        result = AI_MODEL.predict(file_path)
        
        # Calculate actual Severity via OpenCV
        severity = AI_MODEL.calculate_severity(file_path)
        
        # Generate Heatmap
        gradcam_filename = f"heatmap_{filename}"
        gradcam_path = os.path.join(settings.MEDIA_ROOT, 'uploads', gradcam_filename)
        heatmap_success = generate_gradcam(file_path, gradcam_path)
        
        # 5. Clean up string formatting for display
        raw_name = result["top_prediction"]
        if '___' in raw_name:
            crop, disease = raw_name.split('___', 1)
            disease = disease.replace('_', ' ').title()
            
            # Clean up crop names to match database better
            crop = crop.replace('_(maize)', '').replace('_(including_sour)', '').replace('_', ' ').title()
            
            if disease.lower().startswith(crop.lower()):
                clean_name = disease
            else:
                clean_name = f"{crop} {disease}"
        else:
            clean_name = raw_name.replace('_', ' ').title()

        # Update Database
        log.predicted_disease = clean_name
        log.confidence = round(result["confidence"], 2)
        log.alternatives = result["alternatives"]
        log.is_ood = result["is_ood"]
        log.severity = severity
        log.save()
        
        # SMS Alert
        farmer_phone = request.user.phone 
        if farmer_phone and not result["is_ood"]:
            sms_message = f"AgriScan Alert: Your crop has been diagnosed with {clean_name} ({log.confidence}% confidence)."
            send_sms(farmer_phone, sms_message)
        
                # 8. Fetch Disease Info (BULLETPROOF FALLBACK)
        try:
            # 1. Try exact match
            disease_info = Disease.objects.get(name__iexact=clean_name)
        except Disease.DoesNotExist:
            # 2. Try a fuzzy match (ignores "(maize)" etc.)
            base_disease = disease if '___' in raw_name else clean_name
            disease_info = Disease.objects.filter(name__icontains=base_disease).first()
            
            if not disease_info:
                # 3. Absolute Fallback: NEVER show "Information not available"
                disease_info = Disease(
                    name=clean_name,
                    description=f"The AI detected symptoms matching {clean_name}. Specific agronomic data for this exact class is being updated in our database.",
                    treatment="Apply a broad-spectrum organic fungicide or bactericide. Immediately remove and destroy heavily infected leaves to prevent spread.",
                    prevention="Ensure proper plant spacing for air circulation, avoid overhead watering, and practice crop rotation.",
                    dosage_instructions="Mix 2ml of liquid copper fungicide per 1 liter of water. Spray during early morning or late evening.",
                    safety_advisory="Always wear protective clothing, gloves, and a mask. Avoid spraying near water bodies to protect aquatic life."
                )
            
        search_keyword = clean_name.split()[-1]
        recommended_products = Product.objects.filter(name__icontains=search_keyword)[:3]

        return render(request, 'result.html', {
            'log': log,
            'disease': disease_info,
            'recommended_products': recommended_products,
            'gradcam_image': f"/media/uploads/{gradcam_filename}" if heatmap_success else None,
            'needs_review': result["needs_review"]
        })
        
    # 3. Handle GET requests (Home Page Dashboard)
    if request.user.is_authenticated:
        recent_scans = PredictionLog.objects.filter(user=request.user).order_by('-date_uploaded')[:3]
        all_user_scans = PredictionLog.objects.filter(user=request.user)
        total_scans = all_user_scans.count()
        healthy_count = all_user_scans.filter(predicted_disease__icontains='healthy').count()
        diseased_count = total_scans - healthy_count

        from .models import CropCycle
        active_crops = CropCycle.objects.filter(farmer=request.user, is_active=True)[:3]
    else:
        # Empty data for anonymous users
        recent_scans = []
        total_scans = 0
        healthy_count = 0
        diseased_count = 0
        active_crops = []

    top_products = Product.objects.all().order_by('?')[:3] 
    latest_post = ForumPost.objects.order_by('-id').first()
    
    # --- NEW FEATURE 1: Weather Alert ---
    weather_alert = get_disease_risk_alert()

    # --- NEW FEATURE 2: Market Price Logic ---
    market_data = []
    # Get the 3 most recently updated crops
    unique_crops = MarketPrice.objects.values_list('crop_name', flat=True).distinct()[:3]
    
    for crop in unique_crops:
        # Get today's price
        latest_price = MarketPrice.objects.filter(crop_name=crop).order_by('-date', '-id').first()
        # Get 7-day average
        avg_price = MarketPrice.objects.filter(crop_name=crop).aggregate(Avg('price_per_quintal'))['price_per_quintal__avg']
        
        
        if latest_price and avg_price:
            recommendation = "Hold"
            color = "#F59E0B" # Orange
            # Convert Decimal to float for comparison
            avg_price_float = float(avg_price) 
            latest_price_float = float(latest_price.price_per_quintal)
            
            if latest_price_float > avg_price_float * 1.05: # 5% above average
                recommendation = "Sell Now"
                color = "#10B981" # Green
            elif latest_price_float < avg_price_float * 0.95: # 5% below average
                recommendation = "Wait"
                color = "#EF4444" # Red
                
            market_data.append({
                'crop': crop,
                'price': f"{latest_price_float:.0f}",
                'recommendation': recommendation,
                'color': color
            })
    
    return render(request, 'upload.html', {
        'recent_scans': recent_scans,
        'top_products': top_products,
        'latest_post': latest_post,
        'total_scans': total_scans,
        'healthy_count': healthy_count,
        'diseased_count': diseased_count,
        'active_crops': active_crops,
        'weather_alert': weather_alert,
        'market_data': market_data, # <-- Added to context
    })


def history(request):
    if not request.user.is_authenticated:
        return redirect('login')
    logs = PredictionLog.objects.filter(user=request.user).order_by('-date_uploaded')
    return render(request, 'history.html', {'logs': logs})
  
def custom_logout(request):
    logout(request)
    return redirect('login')

def admin_dashboard(request):
    if not request.user.is_authenticated or (request.user.role != 'admin' and not request.user.is_superuser):
        return redirect('home')
        
    User = get_user_model()
    total_scans = PredictionLog.objects.count()
    total_users = User.objects.count()
    total_orders = Order.objects.count()
    total_consultations = ExpertConsultation.objects.count()
    common_diseases = PredictionLog.objects.values('predicted_disease').annotate(count=Count('predicted_disease')).order_by('-count')[:5]
    recent_scans = PredictionLog.objects.order_by('-id')[:5]
    
    context = {
        'total_scans': total_scans,
        'total_users': total_users,
        'total_orders': total_orders,
        'total_consultations': total_consultations,
        'common_diseases': common_diseases,
        'recent_scans': recent_scans,
    }
    return render(request, 'admin_dashboard.html', context)

def scan_detail(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    log = get_object_or_404(PredictionLog, id=pk, user=request.user)
    
    # Regenerate the heatmap if it doesn't exist
    gradcam_filename = f"heatmap_{log.image.name.split('/')[-1]}"
    gradcam_path = os.path.join(settings.MEDIA_ROOT, 'uploads', gradcam_filename)
    
    if not os.path.exists(gradcam_path) and os.path.exists(log.image.path):
        generate_gradcam(log.image.path, gradcam_path)
        
    heatmap_success = os.path.exists(gradcam_path)

    try:
        disease_info = Disease.objects.get(name__iexact=log.predicted_disease)
    except Disease.DoesNotExist:
        disease_info = Disease(
            name=log.predicted_disease, 
            description="Information unavailable.", 
            treatment="Consult an expert.", 
            prevention="Monitor the plant.",
            dosage_instructions="N/A",
            safety_advisory="N/A"
        )
        
    search_keyword = log.predicted_disease.split()[-1]
    recommended_products = Product.objects.filter(name__icontains=search_keyword)[:3]

    return render(request, 'result.html', {
        'log': log,
        'disease': disease_info,
        'recommended_products': recommended_products,
        'gradcam_image': f"/media/uploads/{gradcam_filename}" if heatmap_success else None
    })

@login_required
def delete_scan(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    
    log = get_object_or_404(PredictionLog, id=pk, user=request.user)
    
    try:
        if os.path.exists(log.image.path):
            os.remove(log.image.path)
        
        heatmap_name = f"heatmap_{log.image.name.split('/')[-1]}"
        heatmap_path = os.path.join(settings.MEDIA_ROOT, 'uploads', heatmap_name)
        if os.path.exists(heatmap_path):
            os.remove(heatmap_path)
    except Exception as e:
        print(f"Error deleting files: {e}")

    log.delete()
    
    messages.success(request, "🗑️ Scan deleted successfully.")
    return redirect('history')


@login_required
def add_crop_cycle(request):
    if request.method == 'POST':
        form = CropCycleForm(request.POST)
        if form.is_valid():
            cycle = form.save(commit=False)
            cycle.farmer = request.user 
            cycle.is_active = True      
            cycle.save()
            messages.success(request, "🌱 Crop cycle added successfully!")
            return redirect('home')
    else:
        form = CropCycleForm()
        
    return render(request, 'add_crop.html', {'form': form})
    
def download_report(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
        
    log = get_object_or_404(PredictionLog, id=pk, user=request.user)
    
    try:
        disease = Disease.objects.get(name__iexact=log.predicted_disease)
    except Disease.DoesNotExist:
        disease = None

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], textColor=colors.HexColor("#059669"), spaceAfter=20)
    text_style = styles['Normal']
    
    elements.append(Paragraph("🌱 AgriScan AI - Crop Diagnosis Report", title_style))
    elements.append(Paragraph(f"Date: {log.date_uploaded.strftime('%d %B %Y, %I:%M %p')}", text_style))
    elements.append(Paragraph(f"Scanned by: {request.user.username}", text_style))
    elements.append(Spacer(1, 20))
    
    if log.image:
        img = Image(log.image.path, width=300, height=200)
        elements.append(img)
        elements.append(Spacer(1, 20))
        
    data = [
        ['Detected Condition:', log.predicted_disease.replace('_', ' ')],
        ['AI Confidence:', f"{log.confidence}%"],
        ['Severity (Leaf Area):', f"{log.severity}%"],
    ]
    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#ECFDF5")),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#065F46")),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    if disease:
        elements.append(Paragraph("Description", styles['Heading3']))
        elements.append(Paragraph(disease.description, text_style))
        elements.append(Spacer(1, 10))
        
        elements.append(Paragraph("Treatment", styles['Heading3']))
        elements.append(Paragraph(disease.treatment, text_style))
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("Dosage Instructions", styles['Heading3']))
        elements.append(Paragraph(disease.dosage_instructions or "N/A", text_style))
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("Ecosystem Safety", styles['Heading3']))
        elements.append(Paragraph(disease.safety_advisory or "N/A", text_style))
        elements.append(Spacer(1, 10))
        
        elements.append(Paragraph("Prevention", styles['Heading3']))
        elements.append(Paragraph(disease.prevention, text_style))
        
    doc.build(elements)
    buffer.seek(0)
    
    return FileResponse(buffer, as_attachment=True, filename=f"AgriScan_Report_{log.id}.pdf")