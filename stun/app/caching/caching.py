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
    all_nat_world = "all_nat_world"
    v4_nat = "v4_nat"
    v4_nat_world = "v4_nat_world"
    v6_nat = "v6_nat"
    v6_nat_world = "v6_nat_world"

    v6_only = "v6_only"
    v6_only_world = "v6_only_world"

    v6_with_v4_capacity = "v6_with_v4_capacity"
    v6_with_v4_capacity_world = "v6_with_v4_capacity_world"
    dualstack = "dualstack"
    dualstack_world = "dualstack_world"
    npt = "npt"
    npt_world = "npt_world"
    country_participation = "country_participation"

    public_pfxs_nat_free_0_false_percentage = "public_pfxs_nat_free_0_false_percentage"

    private_prefixes = "private_prefixes"
    announcements = "announcements"


class LocalCacheProxy(DefaultCacheProxy):

    keys = CacheKeys()

    def get_or_set(self, key, call, params={}):
        """
        :param key:
        :param call:
        :return:
        """
        HOURS = 3600
        forever = None
        cached = self.get(key)
        hit=True
        if cached is None:
            hit=False
            cached = call(**params)
            self.set(key, cached, 25*HOURS)

        statsd.increment(
            'cache-hit',
            tags=[
                     'key:' + key,
                     'hit:' + str(hit).lower()
                 ] + DATADOG_DEFAULT_TAGS
        )

        return cached


cache = LocalCacheProxy()
