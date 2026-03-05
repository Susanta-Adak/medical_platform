import re

fname = 'questionnaires/views.py'
with open(fname, 'r') as f:
    orig = f.read()

replacement = '''                    elif answer.option_answer.exists():
                        options_text = []
                        for opt in answer.option_answer.all():
                            opt_text = opt.text or ''
                            if getattr(opt, 'option_image', None) and not opt_text:
                                opt_text = '[Image option]'
                            if getattr(opt, 'option_image', None) and opt.option_image:
                                file_url = request.build_absolute_uri(opt.option_image.url) if hasattr(request, 'build_absolute_uri') else opt.option_image.url
                                opt_text += f" (Image URL: {file_url})"
                            options_text.append(opt_text.strip())
                        
                        options = ', '.join(options_text)
                        row.append(options)'''

content = re.sub(
    r"                    elif answer\.option_answer\.exists\(\):\n\s*options = ', '\.join\(\[opt\.text for opt in answer\.option_answer\.all\(\)\]\)\n\s*row\.append\(options\)",
    replacement,
    orig, 
    count=1
)

with open(fname, 'w') as f:
    f.write(content)

