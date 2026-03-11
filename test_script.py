import os
import django
import sys

sys.path.append('/Users/annjan/Desktop/cursor/medical_platform')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questionnaires.models import Questionnaire
import json

q = Questionnaire.objects.get(id=8)
all_questions = list(q.questions.all().order_by('order', 'id'))
questions_data = []
for question in all_questions:
    question_data = {
        'id': question.id,
        'question_text': question.question_text,
        'type': question.question_type,
        'required': question.is_required,
        'allow_multiple_selections': question.allow_multiple_selections,
        'order': question.order,
        'parent_id': question.parent_id if question.parent else None,
        'trigger_answer': question.trigger_answer,
        'display_number': question.get_display_number(),
        'reference_image_url': question.reference_image.url if question.reference_image else None
    }
    
    if question.question_type == 'multiple_choice':
        question_data['options'] = [
            {
                'text': opt.text,
                'order': opt.order
            }
            for opt in question.options.all()
        ]
    questions_data.append(question_data)

print(json.dumps(questions_data, indent=2))
