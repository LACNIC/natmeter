from django.core.cache import DefaultCacheProxy
from datadog import statsd
from stun.settings import DATADOG_DEFAULT_TAGS

class CacheKeys():
    """
    Place to list all cached keys
    """
    v6_avg = "v6_avg"
    v4_avg = "v4_avg"
    v6_max = "v6_max"
    v4_max = "v4_max"
    all_nat = "all_nat"
    v4_nat = "v4_nat"
    v6_nat = "v6_nat"
    v6_with_v4_capacity = "v6_with_v4_capacity"
    dualstack = "dualstack"
    npt = "npt"
    # nat_pressure = "nat_pressure"
    country_participation = "country_participation"
    private_prefixes = "private_prefixes"
    announcements = "announcements"


class LocalCacheProxy(DefaultCacheProxy):

    keys = CacheKeys()

    def get_or_set(self, key, call):
        """
        :param key:
        :param call:
        :return:
        """
        forever = None
        cached = self.get(key)
        hit=True
        if cached is None:
            hit=False
            cached = call()
            self.set(key, cached, forever)

        statsd.increment(
            'cache-hit',
            tags=[
                     'key:' + key,
                     'hit:' + str(hit).lower()
                 ] + DATADOG_DEFAULT_TAGS
        )

        return cached


cache = LocalCacheProxy()
