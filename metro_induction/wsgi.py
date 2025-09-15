"""
WSGI config for metro_induction project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'metro_induction.settings')

application = get_wsgi_application()