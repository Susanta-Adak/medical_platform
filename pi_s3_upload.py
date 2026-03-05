import subprocess
import requests
import json
import zipfile
import os

# CONFIGURATION (Should match what the Pi is assigned)
DJANGO_SERVER_URL = "http://localhost:8000/iot"
DEVICE_ID = "MDCD001"
SESSION_ID = 5

def create_mock_zip(zip_name="patient_data.zip"):
    """Generates a dummy .zip file locally to represent medical data."""
    print(f"📦 Simulating an Ultrasound Scan and packaging into {zip_name}...")
    with open("dummy_scan.txt", "w") as f:
        f.write("Simulated Ultrasonic Scan Results Data.")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write("dummy_scan.txt")
        
    os.remove("dummy_scan.txt")
    print(f"✅ {zip_name} packaged successfully! Size: {os.path.getsize(zip_name)} bytes.")
    return zip_name


def upload_zip_to_s3(zip_filepath):
    """
    Step 1: Asks Django for an AWS S3 Presigned URL.
    Step 2: Uploads the direct binary to AWS S3.
    Step 3: Notifies Django that the upload is complete.
    """
    print("\n--- INITIATING CLOUD UPLOAD SEQUENCE ---")
    
    # [STEP 1] Ask Django Server for permission/location
    print(f"�� Requesting S3 presigned URL from {DJANGO_SERVER_URL}/session/upload/init/...")
    init_res = requests.post(f"{DJANGO_SERVER_URL}/session/upload/init/", json={
        "device_id": DEVICE_ID,
        "session_token": "abc-123-xyz" # Dummy session token for security
    })
    
    if init_res.status_code != 200:
        print(f"❌ Server rejected init request: {init_res.text}")
        return
        
    init_data = init_res.json()
    upload_url = init_data.get("upload_url")
    upload_fields = init_data.get("upload_fields", {})
    object_name = init_data.get("object_name")
    
    print(f"✅ Received temporary 1-Hour AWS S3 Presigned POST payload!")
    print(f"   Target S3 Key: {object_name}")
    
    # [STEP 2] Direct POST to AWS S3 using multipart/form-data
    print("🚀 Bypassing Django! Uploading ZIP directly to Amazon S3...")
    with open(zip_filepath, 'rb') as f:
        # For presigned POS, we pass the amazon fields as data and the file in 'files' dict
        s3_res = requests.post(upload_url, data=upload_fields, files={'file': f})
        
    if s3_res.status_code not in (200, 204):
        print(f"❌ Direct S3 Upload Failed: {s3_res.status_code} {getattr(s3_res, 'text', '')}")
        return
        
    print("✅ High-speed S3 Upload successful! File is safe in the cloud.")
    
    # [STEP 3] Notify Django that the job is done so the HA can download it
    print(f"🔔 Notifying Django Backend at {DJANGO_SERVER_URL}/session/upload/done/...")
    done_res = requests.post(f"{DJANGO_SERVER_URL}/session/upload/done/", json={
        "device_id": DEVICE_ID,
        "session_id": SESSION_ID,
        "object_name": object_name
    })
    
    if done_res.status_code == 200:
        print("🎉 SUCCESS! Backend mapped the ZIP to the Patient Session.")
    else:
        print(f"❌ Backend mapping failed: {done_res.text}")
        
    print("----------------------------------------\n")

if __name__ == "__main__":
    generated_zip = create_mock_zip("ultrasound_payload.zip")
    upload_zip_to_s3(generated_zip)
    
    # Cleanup dummy file
    if os.path.exists(generated_zip):
        os.remove(generated_zip)
