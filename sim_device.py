import paho.mqtt.client as mqtt
import time
import json
import uuid
import sys
import requests

BROKER = "localhost" 
PORT = 1883
DEVICE_ID = "MDCD001" 
SERVER_URL = "http://localhost:8000"

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    print("Sending ACTIVE status...")
    client.publish(f"device/{DEVICE_ID}/status", json.dumps({
        "status": "online",
        "timestamp": time.time()
    }))

def on_message(client, userdata, msg):
    print(f"\n[RECEIVED] Topic: {msg.topic}")
    payload = msg.payload.decode() if msg.payload else ""
    print(f"[RECEIVED] Payload: {payload}")
    
    try:
        if "ping" in msg.topic:
            print(f"--> Received Ping! Sending heartbeat response...")
            client.publish(f"device/{DEVICE_ID}/heartbeat", json.dumps({
                "status": "online",
                "timestamp": time.time()
            }))
            return

        # It's a scan trigger if it has the format DEVICE_ID/SESSION_ID/SCAN_TYPE
        parts = msg.topic.split('/')
        if len(parts) == 3 and parts[0] == DEVICE_ID:
            session_id = parts[1]
            scan_type = parts[2]
            
            print(f"--> Received Trigger request ({scan_type}) for Session {session_id}!")
            time.sleep(1)
            
            if scan_type in ['vitals', 'default', None]:
                print(f"--> Pushing Vitals to Server over HTTP...")
                data = {
                    "device_id": DEVICE_ID,
                    "session_id": session_id,
                    "reading_type": "vitals",
                    "value": {"systolic": 120, "diastolic": 80, "heart_rate": 72, "temperature_c": 36.6}
                }
                res = requests.post(f"{SERVER_URL}/iot/receive-text/", json=data)
                print(f"--> Server HTTP Response: {res.status_code}")
                
            elif scan_type == 'image':
                # Fake URL image returned
                print(f"--> Pushing Image URL to Server over HTTP...")
                data = {
                    "device_id": DEVICE_ID,
                    "session_id": session_id,
                    "reading_type": "image",
                    "value": "https://dummyimage.com/600x400/000/fff&text=Simulated+X-RAY"
                }
                res = requests.post(f"{SERVER_URL}/iot/receive-text/", json=data)
                print(f"--> Server HTTP Response: {res.status_code}")
            
    except Exception as e:
        print(f"Error handling message: {e}")

try:
    print(f"Connecting device {DEVICE_ID} to mqtt broker at {BROKER}:{PORT}...")
    client = mqtt.Client(client_id=f"SimDevice_{uuid.uuid4().hex[:8]}")
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect(BROKER, PORT, 60)
    
    client.subscribe(f"{DEVICE_ID}/ping")
    client.subscribe(f"{DEVICE_ID}/#")
    
    client.loop_forever()
except Exception as e:
    print(f"Failed to connect: {e}")
