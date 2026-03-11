import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questionnaires.models import Questionnaire
from django.test import RequestFactory
from django.contrib.auth.models import User
from questionnaires.views_builder import clone_questionnaire

q = Questionnaire.objects.get(id=8)
print("Original version:", q.version)

rf = RequestFactory()
request = rf.post('/questionnaires/8/clone/')
request.user = User.objects.first()

response = clone_questionnaire(request, q.id)
new_q = Questionnaire.objects.all().order_by('-id').first()
print("New version:", new_q.version)
