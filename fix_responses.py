import os
import glob

files = [
    'templates/health_assistant/response_detail.html',
    'templates/questionnaires/response_detail.html',
    'templates/doctor/response_detail.html'
]

replacement = '''                                                {% if option.option_image %}
                                                <div class="mb-2">
                                                    <img src="{{ option.option_image.url }}" alt="Option Image" class="img-thumbnail" style="max-height: 100px;">
                                                    {% if option.text %}
                                                    <span class="badge bg-info mt-1 d-block">{{ option.text }}</span>
                                                    {% endif %}
                                                </div>
                                                {% else %}
                                                <span class="badge bg-info mt-1">{{ option.text }}</span>
                                                {% endif %}'''

replacement_badge_info = '''                      {% if option.option_image %}
                      <div class="mb-2 flex flex-col items-center">
                          <img src="{{ option.option_image.url }}" alt="Option Image" class="img-thumbnail rounded shadow-sm mb-1" style="max-height: 100px;">
                          {% if option.text %}
                          <span class="inline-flex items-center px-2.5 py-1 rounded-md text-sm font-medium bg-blue-50 text-blue-700 border border-blue-100">{{ option.text }}</span>
                          {% endif %}
                      </div>
                      {% else %}
                      <span class="inline-flex items-center px-2.5 py-1 rounded-md text-sm font-medium bg-blue-50 text-blue-700 border border-blue-100">{{ option.text }}</span>
                      {% endif %}'''


for f_path in files:
    if os.path.exists(f_path):
        with open(f_path, 'r') as f:
            content = f.read()
        
        # for templates/health_assistant and templates/doctor (which use badge bg-info)
        content = content.replace(
            '{% for option in answer.option_answer.all %}\n'
            '                                            <span class="badge bg-info mt-1">{{ option.text }}</span>\n'
            '                                            {% endfor %}',
            '{% for option in answer.option_answer.all %}\n' + replacement + '\n                                            {% endfor %}'
        )
        
        # for templates/questionnaires (which uses inline-flex)
        if 'class="inline-flex items-center' in content:
            # Let's perform a smart regex replace to catch the inline-flex string
            import re
            content = re.sub(
                r'{% for option in answer\.option_answer\.all %}\s*<span\s*class="inline-flex items-center px-2\.5 py-1 rounded-md text-sm font-medium bg-blue-50 text-blue-700 border border-blue-100">\s*{{ option\.text }}\s*</span>\s*{% endfor %}',
                '{% for option in answer.option_answer.all %}\n' + replacement_badge_info + '\n                    {% endfor %}',
                content
            )

        # doctor might use badge bg-info or something else
        content = content.replace(
            '{% for option in answer.option_answer.all %}\n'
            '                                    <span class="badge bg-info mt-1">{{ option.text }}</span>\n'
            '                                    {% endfor %}',
            '{% for option in answer.option_answer.all %}\n' + replacement + '\n                                    {% endfor %}'
        )

        with open(f_path, 'w') as f:
            f.write(content)
        print(f"Updated {f_path}")

