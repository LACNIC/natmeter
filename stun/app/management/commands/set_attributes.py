from django.core.management.base import BaseCommand
from app.models import StunMeasurement


class SetAttributesCommand(BaseCommand):
    def handle(self, *args, **options):
        StunMeasurement.objects.set_attributes()
