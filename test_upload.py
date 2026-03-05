import requests

url = "http://localhost:8000/questionnaires/api/save/"
data = {
    "title": "Automated Test Questionnaire",
    "description": "testing 123",
    "questions": [
        {
            "id": "new_1",
            "question_text": "Image test question",
            "type": "multiple_choice",
            "required": True,
            "order": 1,
            "options": [
                {
                    "id": "opt_0_0",
                    "text": "",
                    "order": 1,
                    "image_key": "image_opt_0_0"
                },
                {
                    "id": "opt_0_1",
                    "text": "Fallback text",
                    "order": 2,
                    "image_key": None
                }
            ]
        }
    ]
}

import json
payload = {'data': json.dumps(data)}
files = {'image_opt_0_0': ('blank.png', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\x0d\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82', 'image/png')}

# Note: csrf is disabled for API if possible, or we might get 403. Let's see.
session = requests.Session()
r_get = session.get("http://localhost:8000/health-assistant/login/")
csrf_token = session.cookies.get('csrftoken', '')

# We need to authenticate.
session.post("http://localhost:8000/health-assistant/login/", data={'username': 'healthAssistant', 'password': 'password', 'csrfmiddlewaretoken': csrf_token})

r_post = session.post(url, data=payload, files=files, headers={'X-CSRFToken': session.cookies.get('csrftoken', '')})
print("STATUS:", r_post.status_code)
print("RESPONSE:", r_post.text)

print("Testing Edit feature...")
url_edit = "http://localhost:8000/questionnaires/builder/35/edit/"
r_edit = session.post(url_edit, data=payload, files=files, headers={'X-CSRFToken': session.cookies.get('csrftoken', '')})
print("STATUS:", r_edit.status_code)
print("RESPONSE:", r_edit.text)
