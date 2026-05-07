import os
import io
import uuid
import boto3
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.utils import timezone

def fetch_pdf_resources(uri, rel):
    """
    Callback to allow xhtml2pdf to access Django static files.
    """
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.BASE_DIR, uri.replace(settings.STATIC_URL, 'static/'))
        return path
    elif uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
        return path
    return uri

def generate_prescription_pdf(context):
    import base64
    
    # Check for doctor signature and convert to base64 for reliable PDF embedding
    doctor = context.get('doctor')
    if doctor and hasattr(doctor, 'signature') and doctor.signature:
        try:
            image_data = doctor.signature.read()
            b64 = base64.b64encode(image_data).decode('utf-8')
            ext = doctor.signature.name.split('.')[-1].lower()
            content_type = 'image/png' if ext == 'png' else 'image/jpeg'
            context['doctor_signature_b64'] = f"data:{content_type};base64,{b64}"
        except Exception as e:
            print(f"Failed to fetch signature: {e}")

    template_path = 'doctor/prescription_pdf.html'
    template = get_template(template_path)
    html = template.render(context)
    result = io.BytesIO()
    
    # Generate PDF
    pisa_status = pisa.CreatePDF(
        html, dest=result, link_callback=fetch_pdf_resources
    )
    
    if pisa_status.err:
        raise Exception("PDF generation failed")
        
    return result.getvalue()

def upload_pdf_to_s3(pdf_bytes, identifier):
    """
    Uploads the given PDF bytes to AWS S3.
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
        endpoint_url=getattr(settings, 'AWS_S3_ENDPOINT_URL', None)
    )
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    
    object_name = f"prescriptions/{identifier}.pdf"
    
    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_name,
        Body=pdf_bytes,
        ContentType='application/pdf',
        ACL='private' # or 'public-read' depending on requirements
    )
    
    return object_name

def generate_presigned_url(object_name, expiration=3600):
    from botocore.client import Config
    
    region = getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')
    s3_client_kwargs = {
        'aws_access_key_id': getattr(settings, 'AWS_ACCESS_KEY_ID', None),
        'aws_secret_access_key': getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
        'region_name': region,
        'config': Config(signature_version='s3v4')
    }
    
    # Enforce regional endpoint to prevent AWS Signature/AccessDenied issues in regions like ap-south-1
    if getattr(settings, 'AWS_S3_ENDPOINT_URL', None):
        s3_client_kwargs['endpoint_url'] = settings.AWS_S3_ENDPOINT_URL
    else:
        s3_client_kwargs['endpoint_url'] = f"https://s3.{region}.amazonaws.com"
        
    s3_client = boto3.client('s3', **s3_client_kwargs)
    bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
    
    response = s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': bucket_name,
                                                        'Key': object_name},
                                                ExpiresIn=expiration)
    return response
