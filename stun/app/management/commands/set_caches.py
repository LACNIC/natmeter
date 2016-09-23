from django.core.management.base import BaseCommand
from app.caching.caching import cache as cache
from models import StunMeasurementManager as Manager


class Command(BaseCommand):
    def handle(self, *args, **options):
        cache.set(cache.keys.v6_avg, call=Manager.v6_count_avg)
        cache.set(cache.keys.v4_avg, call=Manager.v4_count_avg)
        cache.set(cache.keys.v6_max, call=Manager.v6_count_max)
        cache.set(cache.keys.v4_max, call=Manager.v4_count_max)
        cache.set(cache.keys.all_nat, call=Manager.nat_stats)
        cache.set(cache.keys.v4_nat, call=Manager.get_v4_nat_percentage)
        cache.set(cache.keys.v6_nat, call=Manager.get_v6_nat_percentage)
        cache.set(cache.keys.v6_with_v4_capacity, call=Manager.get_v6_hosts_with_v4_capability_percentage)
        cache.set(cache.keys.dualstack, call=Manager.get_dualstack_percentage)
        cache.set(cache.keys.npt, call=Manager.get_npt_percentage)
        cache.set(cache.keys.nat_pressure, call=Manager.get_nat_time_pressure)
        cache.set(cache.keys.country_participation, call=Manager.get_country_participation)
