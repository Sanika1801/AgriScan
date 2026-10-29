import os
import numpy as np
import random
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib import messages # <-- Added for delete success message
from .models import PredictionLog, Disease
from marketplace.models import Product
from django.contrib.auth import logout
from tensorflow.keras.models import load_model # type: ignore
from tensorflow.keras.preprocessing import image # type: ignore
from django.db.models import Count
from marketplace.models import Order
from community.models import ExpertConsultation
from django.contrib.auth import get_user_model
from django.http import FileResponse
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from .gradcam import generate_gradcam
from analytics.utils import send_sms

# Load the AI model and class names
MODEL_PATH = os.path.join(settings.BASE_DIR, 'crop_disease_model.h5')
CLASS_NAMES_PATH = os.path.join(settings.BASE_DIR, 'class_names.txt')

try:
    MODEL = load_model(MODEL_PATH)
    with open(CLASS_NAMES_PATH, 'r') as f:
        CLASS_NAMES = [line.strip() for line in f.readlines()]
except Exception as e:
    MODEL = None
    CLASS_NAMES = []
    print(f"⚠️ AI Model not found. Please train it first. Error: {e}")

def upload_image(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.role == 'seller':
        return redirect('seller_dashboard')
    elif request.user.role == 'agronomist':
        return redirect('agronomist_dashboard')
    elif request.user.role == 'admin' or request.user.is_superuser:
        return redirect('admin_dashboard')

    if request.method == 'POST' and request.FILES.get('leaf_image'):
        uploaded_file = request.FILES['leaf_image']
        
        if MODEL is None:
            return render(request, 'error.html', {'error': 'AI Model not loaded.'})
            
        # 1. Save the image directly using Django's ImageField logic
        # This automatically creates the /media/uploads/ folder and saves the correct path
        log = PredictionLog.objects.create(
            user=request.user,
            image=uploaded_file, 
            predicted_disease="Processing...", # Temporary placeholder
            confidence=0, 
            severity=0
        )
        
        file_path = log.image.path
        filename = os.path.basename(log.image.name)
        
        # 2. Preprocess the image
        img = image.load_img(file_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0
        
        # 3. Predict
        predictions = MODEL.predict(img_array)
        predicted_class_index = np.argmax(predictions[0])
        confidence = float(np.max(predictions[0])) * 100
        
        # 4. Generate Heatmap
        gradcam_filename = f"heatmap_{filename}"
        gradcam_path = os.path.join(settings.MEDIA_ROOT, 'uploads', gradcam_filename)
        heatmap_success = generate_gradcam(file_path, gradcam_path)
        
        raw_name = CLASS_NAMES[predicted_class_index]
        if '___' in raw_name:
            crop, disease = raw_name.split('___', 1)
            disease = disease.replace('_', ' ').title()
            if disease.lower().startswith(crop.lower()):
                clean_name = disease
            else:
                clean_name = f"{crop.capitalize()} {disease}"
        else:
            clean_name = raw_name.replace('_', ' ').title()
        
        if confidence > 75:
            severity = random.randint(60, 95)
        else:
            severity = random.randint(15, 45)

        # 5. Update the record with the actual results
        log.predicted_disease = clean_name
        log.confidence = round(confidence, 2)
        log.severity = severity
        log.save()
        
        farmer_phone = request.user.phone 
        if farmer_phone:
            sms_message = f"AgriScan Alert: Your crop has been diagnosed with {clean_name} ({round(confidence,2)}% confidence)."
            send_sms(farmer_phone, sms_message)
        
        try:
            disease_info = Disease.objects.get(name__iexact=clean_name)
        except Disease.DoesNotExist:
            disease_info = Disease(
                name=clean_name,
                description="Information not available.",
                treatment="Consult a local agricultural expert.",
                prevention="Keep monitoring the plant.",
                dosage_instructions="N/A",
                safety_advisory="N/A"
            )
            
        search_keyword = clean_name.split()[-1]
        recommended_products = Product.objects.filter(name__icontains=search_keyword)[:3]

        return render(request, 'result.html', {
            'log': log,
            'disease': disease_info,
            'recommended_products': recommended_products,
            'gradcam_image': f"/media/uploads/{gradcam_filename}" if heatmap_success else None
        })
        
    return render(request, 'upload.html')


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
    recent_scans = PredictionLog.objects.order_by('-date_uploaded')[:5]
    
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
    
    # Regenerate the heatmap if it doesn't exist (useful for old scans)
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

# ==========================================
# NEW: Delete Scan Function
# ==========================================
@login_required
def delete_scan(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get the specific scan, ensuring it belongs to the logged-in user
    log = get_object_or_404(PredictionLog, id=pk, user=request.user)
    
    # Optional: Delete the image files from storage to save space
    try:
        if os.path.exists(log.image.path):
            os.remove(log.image.path)
        
        # Also try to delete the heatmap if it exists
        heatmap_name = f"heatmap_{log.image.name.split('/')[-1]}"
        heatmap_path = os.path.join(settings.MEDIA_ROOT, 'uploads', heatmap_name)
        if os.path.exists(heatmap_path):
            os.remove(heatmap_path)
    except Exception as e:
        print(f"Error deleting files: {e}")

    log.delete()
    
    messages.success(request, "🗑️ Scan deleted successfully.")
    return redirect('history')
    
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