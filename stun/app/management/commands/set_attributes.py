from django.core.management.base import BaseCommand
from app.models import StunMeasurement


class Command(BaseCommand):
    def handle(self, *args, **options):

        force = False
        try:
            force = int(args[0])
            if force == 1:
                force = True
        except:
            pass

        StunMeasurement.objects.set_attributes(force=force)
