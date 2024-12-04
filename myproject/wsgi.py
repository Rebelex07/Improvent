"""
WSGI config for myproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Asegúrate de que el nombre del módulo esté correcto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Improvent.settings')

application = get_wsgi_application()
