from django.core.management.base import BaseCommand
from app.models import StunIpAddress


class ResolveCountriesCommand(BaseCommand):
    def handle(self, *args, **options):
        for ipaddress in StunIpAddress.objects.filter(country='DEF'):  # Default country
            ipaddress.resolve_country(persist=True)
