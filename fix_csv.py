import os
import re

fname = 'health_assistant/views.py'
with open(fname, 'r') as f:
    orig = f.read()

replacement = '''                    elif answer.option_answer.exists():
                        options_text = []
                        for opt in answer.option_answer.all():
                            opt_text = opt.text
                            if getattr(opt, 'option_image', None) and not opt_text:
                                opt_text = '[Image option]'
                            if opt.option_image and opt.option_image.name:
                                file_url = request.build_absolute_uri(opt.option_image.url) if hasattr(request, 'build_absolute_uri') else opt.option_image.url
                                opt_text += f" (Image: {file_url})"
                            elif opt.option_image:
                                opt_text += " [Image]"
                            options_text.append(opt_text)
                        
                        options = ', '.join(options_text)
                        row.append(options)'''

# We need to replace in export_questionnaire_responses_csv
content = re.sub(
r'''                    elif answer.option_answer.exists\(\):\s*options = ', '\.join\(\[opt.text for opt in answer.option_answer.all\(\)\]\)\s*row.append\(options\)''',
replacement,
orig, count=1 )

with open(fname, 'w') as f:
    f.write(content)

