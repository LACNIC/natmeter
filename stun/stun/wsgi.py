"""
WSGI config for stun project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import sys

sys.path.append('/opt/django/natmeter/stun')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stun.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()