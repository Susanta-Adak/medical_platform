import os
import zipfile
import json
import csv
import io
import boto3
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.core.files.base import ContentFile
from devices.models import Device
from patients.models import Patient
from screening.models import ScreeningSession, ScreeningResult, ScreeningAttachment

def process_screening_zip(object_name, session_id):
    """
    Background job to process a ZIP payload in S3.
    Extracts structured data, creates DB rows, and saves media files.
    """
    session = ScreeningSession.objects.filter(id=session_id).first()
    if not session:
        return
        
    s3_client = boto3.client(
        's3',
        aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', 'dummy'),
        aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', 'dummy'),
        region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1'),
        endpoint_url=getattr(settings, 'AWS_S3_ENDPOINT_URL', None) # for minio
    )
    bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'screening-zips')

    try:
        # 1. Download ZIP to memory securely
        zip_obj = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        zip_bytes = io.BytesIO(zip_obj['Body'].read())
        
        with zipfile.ZipFile(zip_bytes) as z:
            # Look for metadata.json first
            if 'metadata.json' in z.namelist():
                meta_file = z.open('metadata.json')
                metadata = json.load(meta_file)
                
                # Context validation logic could apply here
                # if metadata.get('patient_id') != str(session.patient.id):
                #   raise Exception("Patient ID collision detected!")
                
            with transaction.atomic():
                extracted_data = {}
                
                # Process structured & unstructured files
                for filename in z.namelist():
                    data_bytes = z.read(filename)
                    if filename.endswith('.csv'):
                        # Example CSV parser for standard biometric metrics
                        reader = csv.DictReader(io.StringIO(data_bytes.decode('utf-8')))
                        for row in reader:
                            # Build context out of CSV map
                            key = row.get("metric", "unknown")
                            val = row.get("value", "")
                            extracted_data[key] = val
                    
                    elif filename.endswith(('.json')) and filename != 'metadata.json':
                        parsed = json.loads(data_bytes)
                        extracted_data.update(parsed)
                        
                    elif filename.lower().endswith(('.jpg', '.png', '.pdf')):
                        # It's an image/media - Create attachment record natively
                        # In the real world, this could upload the nested file back to S3 cleanly
                        # and tie it structurally to the DB.
                        attachment = ScreeningAttachment(
                            session=session,
                            description=f"Extracted from payload: {filename}"
                        )
                        # The FileField 'file' handles writing bytes safely through Django's storage
                        attachment.file.save(filename, ContentFile(data_bytes), save=True)
                
                # Record unified results back to ScreeningResult model
                ScreeningResult.objects.update_or_create(
                    session=session,
                    defaults={'result_data': extracted_data}
                )

        # 3. Mark successful
        session.upload_status = ScreeningSession.UPLOAD_STATUS_PROCESSED
        session.status = ScreeningSession.STATUS_COMPLETED
        session.save()
        
    except Exception as e:
        session.upload_status = ScreeningSession.UPLOAD_STATUS_FAILED
        session.notes += f"\n[Processing Error]: {str(e)}"
        session.save()
        print(f"Error processing ZIP {object_name}: {e}")
