from django.core.cache import DefaultCacheProxy


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
    nat_pressure = "nat_pressure"
    country_participation = "country_participation"
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
        if cached is None:
            cached = call()
            self.set(key, cached, forever)
        return cached


cache = LocalCacheProxy()
