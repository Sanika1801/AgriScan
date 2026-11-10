from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import PredictionLog
from .predictor import AgriPredictor
import os
from django.conf import settings

# Initialize once
CLASS_NAMES_PATH = os.path.join(settings.BASE_DIR, 'class_names.txt')
with open(CLASS_NAMES_PATH, 'r') as f:
    CLASS_NAMES = [line.strip() for line in f.readlines()]
AI_MODEL = AgriPredictor(os.path.join(settings.BASE_DIR, 'crop_disease_model.h5'), CLASS_NAMES)

class PredictAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('image')
        if not file:
            return Response({"error": "No image uploaded"}, status=400)

        log = PredictionLog.objects.create(
            user=request.user, image=file, predicted_disease="Processing...", confidence=0, severity=0
        )
        
        # Run AI
        result = AI_MODEL.predict(log.image.path)
        severity = AI_MODEL.calculate_severity(log.image.path)
        
        log.predicted_disease = result["top_prediction"]
        log.confidence = result["confidence"]
        log.alternatives = result["alternatives"]
        log.is_ood = result["is_ood"]
        log.severity = severity
        log.save()

        return Response({
            "id": log.id,
            "status": "unknown_image" if result["is_ood"] else "ok",
            "top_prediction": result["top_prediction"],
            "confidence": result["confidence"],
            "alternatives": result["alternatives"],
            "severity": severity
        })