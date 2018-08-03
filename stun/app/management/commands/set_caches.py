from django.core.management.base import BaseCommand
from app.caching.caching import cache as cache
from app.models import StunMeasurement


class Command(BaseCommand):
    def handle(self, *args, **options):
        cache.set(cache.keys.v6_avg, StunMeasurement.objects.v6_count_avg())
        cache.set(cache.keys.v4_avg, StunMeasurement.objects.v4_count_avg())
        cache.set(cache.keys.v6_max, StunMeasurement.objects.v6_count_max())
        cache.set(cache.keys.v4_max, StunMeasurement.objects.v4_count_max())
        cache.set(cache.keys.all_nat, StunMeasurement.objects.nat_stats())
        cache.set(cache.keys.v4_nat, StunMeasurement.objects.get_v4_nat_percentage())
        cache.set(cache.keys.v6_nat, StunMeasurement.objects.get_v6_nat_percentage())
        cache.set(cache.keys.v6_with_v4_capacity, StunMeasurement.objects.get_v6_hosts_with_v4_capability_percentage())
        cache.set(cache.keys.dualstack, StunMeasurement.objects.get_dualstack_percentage())
        cache.set(cache.keys.npt, StunMeasurement.objects.get_npt_percentage())
        # cache.set(cache.keys.nat_pressure, StunMeasurement.objects.get_nat_time_pressure())
        cache.set(cache.keys.country_participation, StunMeasurement.objects.get_country_participation())
        cache.set(cache.keys.announcements, get_announcements())
        cache.set(cache.keys.private_prefixes, StunMeasurement.objects.get_private_pfx_counter())


def get_announcements():
    import csv
    import requests
    import StringIO
    from collections import defaultdict

    CC = 1
    ALLOC = 2
    ADV = 7
    data = requests.get('http://labs.apnic.net/dists/v4.csv').text

    announcements = defaultdict(int)
    csvreader = csv.reader(StringIO.StringIO(data))
    for i in range(16):
        csvreader.next()
    for line in csvreader:
        #     line[CC], line[ALLOC], line[ADV]
        try:
            announcements[line[CC]] = line[ADV]
        except IndexError as e:
            continue
    return announcements
