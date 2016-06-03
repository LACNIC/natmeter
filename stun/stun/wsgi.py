"""
WSGI config for stun project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os, sys
from django.core.wsgi import get_wsgi_application

sys.path.append('/opt/django/stun/stun')
sys.path.append('/Users/agustin/git/stun/stun/stun')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stun.settings")

application = get_wsgi_application()











# os.environ['DJANGO_SETTINGS_MODULE'] = 'simon_project.settings'
