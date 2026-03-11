import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from questionnaires.views_builder import clone_questionnaire
from questionnaires.models import Questionnaire

rf = RequestFactory()
request = rf.post('/questionnaires/8/clone/')
request.user = User.objects.first()

response = clone_questionnaire(request, 8)
print("Status Code:", response.status_code)
print("Location:", response.get('Location'))

q = Questionnaire.objects.latest('id')
print("New Questionnaire:", q.id, q.title, q.version, "Questions:", q.questions.count())
