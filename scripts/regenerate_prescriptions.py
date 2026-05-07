import os
import sys
import django

# Add the project directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod") # or dev/base depending on environment
django.setup()

import re
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from patients.models import Document, PatientNote, MedicalRecord
from doctor.pdf_utils import generate_prescription_pdf, upload_pdf_to_s3

from django.utils import timezone

notes = PatientNote.objects.filter(note_type=PatientNote.NoteType.CONSULTATION)
print(f"Found {notes.count()} consultation notes to process.")

for note in notes:
    patient = note.patient
    
    if not patient.setu_id:
        print(f"Skipping Note ID {note.id} - Patient has no setu_id.")
        continue
        
    content = note.content
    
    diagnosis = ""
    investigations = ""
    advice = ""
    exam_notes = ""
    followup_required = "No"
    
    diag_match = re.search(r'<strong>Provisional Diagnosis</strong><br>(.*?)(?:<br><br>|$)', content, re.DOTALL)
    if diag_match: diagnosis = diag_match.group(1).strip()
    
    inv_match = re.search(r'<strong>Investigations</strong><br>(.*?)(?:<br><br>|$)', content, re.DOTALL)
    if inv_match: investigations = inv_match.group(1).strip()
    
    adv_match = re.search(r'<strong>Advice</strong><br>(.*?)(?:<br><br>|$)', content, re.DOTALL)
    if adv_match: advice = adv_match.group(1).strip()
    
    exam_match = re.search(r'<strong>On Examination</strong><br>(.*?)(?:<br><br>|$)', content, re.DOTALL)
    if exam_match: exam_notes = exam_match.group(1).strip()
    
    fup_match = re.search(r'<strong>Further Followup Required</strong><br>(Yes|No)', content)
    if fup_match: followup_required = fup_match.group(1)
    
    prescriptions_text = ""
    pres_match = re.search(r'<strong>Prescriptions</strong><br>(.*?)(?:<br><br>|$)', content, re.DOTALL)
    pdf_medicines = []
    
    if pres_match:
        pres_block = pres_match.group(1)
        lines = pres_block.split('<br>')
        for line in lines:
            if not line.strip(): continue
            clean = re.sub(r'<[^>]+>', '', line).replace('&bull;', '').strip()
            parts = clean.split('|')
            if len(parts) >= 4:
                first_part = parts[0].split(':')
                typ = first_part[0].strip() if len(first_part) > 1 else ""
                med = first_part[1].strip() if len(first_part) > 1 else first_part[0].strip()
                dos = parts[1].strip()
                dur = parts[2].replace('days', '').strip()
                ins = parts[3].strip()
                oth = parts[4].strip() if len(parts) > 4 else ""
                
                pdf_medicines.append({
                    'type': typ,
                    'name': med,
                    'dose': dos,
                    'instructions': ins,
                    'duration': dur,
                    'others': oth
                })

    medical_record = MedicalRecord.objects.filter(patient=patient).first()
    vitals = patient.vitals.order_by('-recorded_at').first()

    context = {
        'patient': patient,
        'date': note.created_at.strftime("%d %b %Y, %I:%M %p"),
        'vitals': vitals,
        'medical_history': medical_record.chronic_conditions if medical_record else "None",
        'family_history': medical_record.family_history if medical_record else "None",
        'medications': medical_record.current_medications if medical_record else "None",
        'allergies': medical_record.allergies if medical_record else "None",
        'diagnosis': diagnosis,
        'medicines': pdf_medicines,
        'investigations': investigations,
        'advice': advice,
        'followup_required': followup_required,
        'notes': exam_notes,
        'assistant_name': "-", 
        'doctor': note.author,
    }
    
    try:
        pdf_bytes = generate_prescription_pdf(context)
        
        # Check if a Document already exists for this patient, otherwise create one
        doc = Document.objects.filter(patient=patient, document_type=Document.DocumentType.PRESCRIPTION).first()
        if not doc:
            doc = Document(
                patient=patient,
                uploaded_by=note.author,
                document_type=Document.DocumentType.PRESCRIPTION,
                title=f"Prescription - {timezone.now().strftime('%Y-%m-%d')}"
            )
        
        identifier = patient.setu_id
        try:
            object_name = upload_pdf_to_s3(pdf_bytes, identifier)
            doc.description = object_name
            doc.save()
            print(f"Generated and uploaded to S3: Note ID {note.id} -> Doc ID {doc.id} for SETU ID {identifier}")
        except Exception as aws_e:
            doc.file.save(f"prescriptions/{identifier}.pdf", ContentFile(pdf_bytes))
            doc.save()
            print(f"Generated locally: Note ID {note.id} -> Doc ID {doc.id} for SETU ID {identifier}")
            
    except Exception as e:
        print(f"Failed to generate PDF for Note ID {note.id}: {e}")

print("Done generating prescriptions.")
