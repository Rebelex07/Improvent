"""
WSGI config for myproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys

# Añadir el directorio de tu proyecto al path para poder importar los módulos
path = '/home/sergio07god/Improvent'
if path not in sys.path:
    sys.path.append(path)

# Establecer el DJANGO_SETTINGS_MODULE
os.environ['DJANGO_SETTINGS_MODULE'] = 'Improvent.settings'

# Obtener la aplicación WSGI de Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
