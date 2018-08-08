from django.core.management.base import BaseCommand
from app.caching.caching import cache
from app.models import StunMeasurement
from statsd import StatsClient
from stun import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        old = cache.set

        statsd = StatsClient()

        @statsd.timer('cache.set')
        def new(k, v, t=None):
            HOURS = 3600
            print "Setting {key}".format(key=k)
            old(k, v, timeout=25 * HOURS if not settings.DEBUG else None)

        cache.set = new

        cache.set(cache.keys.v6_avg, StunMeasurement.objects.v6_count_avg())
        cache.set(cache.keys.v4_avg, StunMeasurement.objects.v4_count_avg())
        cache.set(cache.keys.v6_max, StunMeasurement.objects.v6_count_max())
        cache.set(cache.keys.v4_max, StunMeasurement.objects.v4_count_max())

        cache.set(cache.keys.all_nat, StunMeasurement.objects.nat_0_percentage(consider_country=True))
        cache.set(cache.keys.all_nat_world, StunMeasurement.objects.nat_0_percentage(consider_country=False))

        cache.set(cache.keys.v4_nat, StunMeasurement.objects.nat_4_percentage(consider_country=True))
        cache.set(cache.keys.v4_nat_world, StunMeasurement.objects.nat_4_percentage(consider_country=False))
        # cache.set(cache.keys.v4_nat, StunMeasurement.objects.get_v4_nat_percentage(consider_country=True))
        # cache.set(cache.keys.v4_nat_world, StunMeasurement.objects.get_v4_nat_percentage(consider_country=False))
        #
        # cache.set(cache.keys.v6_nat, StunMeasurement.objects.get_v6_nat_percentage(consider_country=True))
        # cache.set(cache.keys.v6_nat_world, StunMeasurement.objects.get_v6_nat_percentage(consider_country=False))

        cache.set(cache.keys.v6_only, StunMeasurement.objects.v6_only_percentage(consider_country=False))

        cache.set(cache.keys.v6_with_v4_capacity, StunMeasurement.objects.get_v6_hosts_with_v4_capability_percentage(consider_country=True))
        cache.set(cache.keys.v6_with_v4_capacity_world, StunMeasurement.objects.get_v6_hosts_with_v4_capability_percentage(consider_country=False))

        cache.set(cache.keys.dualstack, StunMeasurement.objects.get_dualstack_percentage(consider_country=True))
        cache.set(cache.keys.dualstack_world, StunMeasurement.objects.get_dualstack_percentage(consider_country=False))

        cache.set(cache.keys.npt, StunMeasurement.objects.get_npt_percentage(consider_country=True))
        cache.set(cache.keys.npt_world, StunMeasurement.objects.get_npt_percentage(consider_country=False))

        cache.set(cache.keys.public_pfxs_nat_free_0_false_percentage, StunMeasurement.objects.public_pfxs_nat_0_false_percentage())

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
