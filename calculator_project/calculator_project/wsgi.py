"""
WSGI config for calculator_project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calculator_project.settings')
application = get_wsgi_application()
