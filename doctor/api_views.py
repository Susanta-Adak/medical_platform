from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from patients.models import Patient, Document
from doctor.pdf_utils import generate_presigned_url
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_GET
def setu_prescription_api(request, identifier):
    """
    API for SETU to fetch the latest prescription for a patient.
    Requires setu_id (or patient_id) in URL.
    Returns the presigned S3 URL for the PDF.
    """
    try:
        # Try fetching by setu_id first, then fallback to patient_id
        patient = Patient.objects.filter(setu_id=identifier).first()
        if not patient:
            patient = Patient.objects.get(patient_id=identifier)
        
        # Get the latest prescription document
        latest_prescription = Document.objects.filter(
            patient=patient,
            document_type=Document.DocumentType.PRESCRIPTION
        ).order_by('-uploaded_at').first()
        
        if not latest_prescription:
            return JsonResponse({'status': 'error', 'message': 'No prescription found for this patient'}, status=404)
            
        # The object name in S3 is saved to the description or file name
        object_name = latest_prescription.description
        if not object_name or not object_name.startswith('prescriptions/'):
            # Fallback
            object_name = latest_prescription.file.name if latest_prescription.file else ""
            
        try:
            url = generate_presigned_url(object_name)
        except Exception as aws_e:
            logger.warning(f"Failed to generate AWS presigned URL: {str(aws_e)}")
            url = request.build_absolute_uri(latest_prescription.file.url) if latest_prescription.file else None

        return JsonResponse({
            'status': 'success',
            'setu_id': patient.setu_id,
            'prescription_url': url,
            'uploaded_at': latest_prescription.uploaded_at.isoformat()
        })
        
    except Patient.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Patient not found'}, status=404)
    except Exception as e:
        logger.error(f"Error fetching prescription: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
