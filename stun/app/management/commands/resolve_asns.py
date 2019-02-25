from django.core.management.base import BaseCommand
from app.models import StunMeasurement


class Command(BaseCommand):
    def handle(self, *args, **options):
        StunMeasurement.objects.resolve_announcing_asns()
