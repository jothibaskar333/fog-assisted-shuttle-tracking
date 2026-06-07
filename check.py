import os

base = os.path.dirname(os.path.abspath(__file__))
templates = os.path.join(base, 'templates')

print("app.py is located at:", base)
print("Looking for templates at:", templates)
print("Templates folder exists?", os.path.exists(templates))

if os.path.exists(templates):
    print("Files inside templates/:", os.listdir(templates))
else:
    print("ERROR: templates folder not found!")