# Medical Data Collection & IoT Platform

A professional-grade healthcare platform designed for secure medical data collection, patient management, and IoT device integration.

##  Core Features

- **Health Assistant Portal**: Streamlined interface for clinicians to manage patient registrations and screening sessions.
- **Dynamic Questionnaire Builder**: Advanced tool for admins to create hierarchical, branching clinical surveys with version control.
- **IoT Integration**: Seamless data synchronization from medical devices directly to secure cloud storage (AWS S3) with pre-signed URL authentication.
- **Admin Dashboard**: Comprehensive analytics and submission tracking for medical operators.
- **Responsive Management**: Accessible across desktop, tablet, and mobile devices.

##  Technology Stack

- **Backend**: Django 4.2+ (Python 3.9+)
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Frontend**: Bootstrap 5, Tailwind CSS, Vanilla JS
- **Infrastructure**: Gunicorn, Nginx, AWS S3 (for medical scans)
- **Real-time**: MQTT Gateway for device status synchronization

##  Installation & Setup

### 1. Prerequisites
- Python 3.9+
- PostgreSQL
- Redis (Optional, for caching)

### 2. Environment Setup
Clone the repository and create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory based on `.env.production`:
```env
DEBUG=False
SECRET_KEY=your-secure-key
ALLOWED_HOSTS=your-domain.com
DB_NAME=medical_platform
DB_USER=...
DB_PASSWORD=...
```

### 4. Database Initialization
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 5. Running the Application
**Development:**
```bash
python manage.py runserver
```

**Production:**
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## ☁️ Deployment

Refer to [DEPLOYMENT_GUIDE.md](file:///Users/annjan/Desktop/cursor/medical_platform/DEPLOYMENT_GUIDE.md) for detailed instructions on deploying to AWS EC2 or other cloud providers.

## 🔒 Security & Privacy

This platform implements:
- Encrypted patient data handling.
- Role-based access control (RBAC).
- Secure IoT data pipelines bypassing common application bottlenecks.
- AWS S3 pre-signed URLs for direct, secure file uploads.

---
© 2026 Medical Data Collection Systems
