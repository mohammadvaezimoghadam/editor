"""
WSGI config for testapp project.
It exposes the WSGI callable as a module-level variable named ``application``.
"""
import os
import sys

# Ensure project and tests directory are in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testapp.settings")

application = get_wsgi_application()
