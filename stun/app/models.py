from __future__ import unicode_literals
from libraries.classes import *
from django.db import models
from django.utils.timezone import now
from ipaddr import *
from collections import Counter
from app.libraries.geolocation import get_cc_from_ip_address
from static_defs import NOISY_PREFIXES
from datetime import timedelta


class StunMeasurementManager(models.Manager):
    def get_average(self, _list=[]):
        return 1.0 * sum(_list) / len(_list)

    def get_max(self, _list=[]):
        return max(_list)

    def get_results(self, days_ago=60):  # everythin in the last 60 days
        """
        @days_ago: time window going backwards. 0 means infinity (all data)
        :return: Get clean results ready for doing stats
        """
        now = datetime.now()
        _all = StunMeasurement.objects.order_by(
            'cookie', '-server_test_date'
        )

        _all_cookie_not_empty = _all.exclude(
            cookie__exact=''
        )#.distinct(
        #     'cookie'
        # )

        _all_empty_cookie = _all.filter(
            cookie__exact=''
        )

        if days_ago != 0:
            since = now - timedelta(days=days_ago)
        else:
            since = datetime(day=1, month=1, year=2010) # start of measurements
        _all_combined = (_all_cookie_not_empty | _all_empty_cookie).filter(
            server_test_date__gte=since
        )

        return [a for a in _all_combined if not a.has_noisy_prefix()]

    def get_v6_results(self):
        """
        :return: All StunMeasurements that have shown IPv6 support
        """
        return [s for s in self.get_results() if s.v6_count() > 0]

    def get_v4_results(self):
        """
        :return: All StunMeasurements that have shown IPv4 support
        """
        return [s for s in self.get_results() if s.v4_count() > 0]

    def get_dualstack_results(self):
        """
        :return: All StunMeasurements that have shown IPv4 and IPv6 support
        """
        return [s for s in self.get_results() if s.v4_count() > 0 and s.v6_count() > 0]

    def get_dualstack_percentage(self):
        ds = StunMeasurement.objects.get_dualstack_results()
        _all = StunMeasurement.objects.get_results()
        return 100.0 * len(ds) / len(_all)

    def v6_count(self):
        """
        :return: All v6_counts (# of addresses) for StunMeasurements that have shown IPv6 support
        """
        return [s.v6_count() for s in self.get_v6_results()]

    def v6_count_avg(self):
        count = self.v6_count()
        return self.get_average(count)

    def v6_count_max(self):
        count = self.v6_count()
        return self.get_max(count)

    def v4_count(self):
        """
        :return: All v4_counts for StunMeasurements that have shown IPv4 support
        """
        return [s.v4_count() for s in self.get_results() if s.v4_count() > 0]

    def v4_count_avg(self):
        count = self.v4_count()
        return self.get_average(count)

    def v4_count_max(self):
        count = self.v4_count()
        return self.get_max(count)

    def get_v6_nat_percentage(self):
        """
        :return: NAT % (percentage) for NAT 66
        """
        v6 = self.get_v6_results()
        natted = [s for s in v6 if s.is_natted(protocol=6)]
        return 100.0 * len(natted) / len(v6)

    def get_v4_nat_percentage(self):
        """
        :return: NAT % (percentage) for NAT 44
        """

        from app.caching.caching import cache as custom_cache
        from management.commands.set_caches import get_announcements
        announcements = custom_cache.get_or_set(
            custom_cache.keys.announcements,
            call=get_announcements
        )

        v4 = self.get_v4_results()

        # weigh by country
        total_region_ips = 0
        total_region_natted_ips = 0
        ccs = ['BB', 'KY', 'CU', 'DM', 'DO', 'GD', 'GP', 'HT', 'JM', 'BZ', 'AW', 'BS', 'SV', 'GT', 'HN', 'AR', 'BO',
               'BR', 'CL', 'GY', 'GF', 'EC', 'CO', 'LC', 'VC', 'TT', 'TC', 'VG', 'VI', 'MX', 'MS', 'PR', 'NI', 'PA',
               'PE', 'VE', 'UY', 'SR', 'PY', 'AI', 'AG', 'MQ', 'KN', 'CR',
               'FK']  # list(set([s.get_country() for s in v4]))  # unique countries only
        for cc in ccs:  # TODO only lac announcements
            if cc not in ccs:
                continue

            cc_msms = [s for s in v4 if s.get_country() == cc]
            cc_msms_natted = [s for s in cc_msms if s.is_natted(protocol=4)]
            if len(cc_msms_natted) == 0:
                continue

            adv = int(announcements[cc])  # announced prefixes
            cc_natted_ratio = 1.0 * len(cc_msms_natted) / len(cc_msms)
            adv_natted_ips = adv * cc_natted_ratio
            total_region_ips += adv
            total_region_natted_ips += adv_natted_ips

        return 100.0 * total_region_natted_ips / total_region_ips if total_region_ips > 0 else 0

    def nat_stats(self):
        """
        :return: NAT % (percentage) for any kind of NAT
        """
        _all = self.get_results()
        natted = [s for s in _all if s.is_natted()]
        return 100.0 * len(natted) / len(_all)

    def get_v6_hosts_with_v4_capability_percentage(self):
        """
        :return: v4 capability % (percentage) for v6-only hosts
        """
        v6 = self.get_v6_results()
        is_v4_capable = [s for s in v6 if s.is_v6_with_v4_capabilities()]
        return 100.0 * len(is_v4_capable) / len(v6)

    def get_npt_percentage(self):
        """
        :return: NPT % (percentage) among v6-only hosts
        """
        v6 = self.get_v6_results()
        is_npt = [s for s in v6 if s.is_npt()]
        return 100.0 * len(is_npt) / len(v6)

    def get_distinct_cookies(self):
        """
        :return: List of distinct cookies
        """
        distinct = StunMeasurement.objects.all().distinct('id')
        return [d.cookie for d in distinct]

    def get_nat_time_pressure(self):
        """
        :return:
        """
        dts = []
        cookies = self.get_distinct_cookies()
        for cookie in cookies:
            msms = StunMeasurement.objects.filter(cookie=cookie).order_by('-server_test_date')

            if len(msms) < 2:  # need at least 2 measurements to calculate dt
                continue

            most_recent = None
            for i, m in enumerate(msms):
                if m.is_natted() and most_recent is None:  # choose the most recent natted msm
                    most_recent = m
                elif m.is_natted() and most_recent is not None:  # get the dt
                    if self.disjoint_lists(m.get_remote_addresses(), most_recent.get_remote_addresses()):
                        dts.append(most_recent.server_test_date - m.server_test_date)
                        break
        return dts

    def get_country_participation(self):
        """
        :return: collections.Counter containing country-code keys, and participation values.
        """
        counter = Counter(StunIpAddress.objects.values_list('country', flat=True))
        counter.pop('DEF')
        counter.pop('XX')
        return counter

    def get_private_pfx_counter(self):

        import operator

        results = self.get_results()
        pvt_pfxs = []
        for r in results:
            addresses = r.get_local_addresses()
            world = StunMeasurement.objects.show_addresses_to_the_world(addresses)
            pvt_pfxs += world
        counter = Counter(pvt_pfxs).items()
        return sorted(counter, key=operator.itemgetter(1), reverse=True)

    @staticmethod
    def is_npt(ip1, ip2):

        try:
            v6_1 = IPv6Address(ip1)
            v6_2 = IPv6Address(ip2)
        except AddressValueError:
            return False

        return v6_1.exploded.split(":")[4:] == v6_2.exploded.split(":")[4:]

    @staticmethod
    def disjoint_lists(list_1, list_2):
        for l1 in list_1:
            if l1 in list_2:
                return False
        for l2 in list_2:
            if l2 in list_1:
                return False

        return True

    @classmethod
    def show_addresses_to_the_world(cls, addresses):
        return [StunMeasurement.objects.show_address_to_the_world(a).encode('utf-8') for a in addresses]

    @classmethod
    def show_address_to_the_world(cls, address):
        """
            Strips part of the address to make it public to anyone (for sharing data for example)
        :return: Stripped address
        """

        res = ""
        if ':' in address:
            add = IPv6Address(address=address).exploded.split(':')[:4]
            for a in add:
                res += "%s:" % a
            res += 3 * '0000:'
            res += '0000'
        else:
            add = IPv4Address(address=address).exploded.split('.')[:3]
            for a in add:
                res += "%s." % a
            res += '0'

        return res


class StunMeasurement(models.Model):
    """
        Stun measurement class. Stores the results provided
        by the JavaScript STUN/TURN software probe.
    """
    server_test_date = models.DateTimeField(default=now)
    client_test_date = models.DateTimeField(default=now)

    experiment_id = models.TextField(default="")
    cookie = models.TextField(default="", null=True)
    tester_version = models.IntegerField(default=0)

    objects = StunMeasurementManager()

    def is_v6_only(self):
        """
        :return: True if this host had v6-only interfaces during this STUN measurement. False otherwise.
        """
        local_addresses = self.get_local_addresses()
        for ip in local_addresses:
            if "." in ip:
                return False
        return True

    def has_v4_capabilities(self):
        """
        :return: Has been seen over v4
        """
        remote_addresses = self.get_remote_addresses()
        for ip in remote_addresses:
            if "." in ip:
                return True
        return False

    def is_v6_with_v4_capabilities(self):
        """
        :return: True if this host had v6-only interfaces during this STUN measurement, but has public IPv4
        capabilities. False otherwise.
        """
        return self.has_v4_capabilities() and self.is_v6_only()

    def get_local_v6_stunipaddresses(self):
        """
        :return: A list of v6 LOCAL StunIpAddress from StunMeasurement.
        """
        ips = self.stunipaddress_set.filter(ip_address_kind=StunIpAddress.Kinds.LOCAL)
        v6 = [ip for ip in ips if ":" in ip.ip_address]
        return v6

    def get_local_v6_ipaddresses(self):
        return [ip for ip in self.get_local_addresses() if ":" in ip]

    def get_local_v4_ipaddresses(self):
        return [ip for ip in self.get_local_addresses() if "." in ip]

    def v6_count(self):
        return len(self.get_local_v6_stunipaddresses())

    def get_local_v4_stunipaddresses(self):
        """
        :return: A list of v4 LOCAL StunIpAddress from StunMeasurement.
        """
        ips = self.stunipaddress_set.filter(ip_address_kind=StunIpAddress.Kinds.LOCAL)
        v4 = [ip for ip in ips if "." in ip.ip_address]
        return v4

    def v4_count(self):
        return len(self.get_local_v4_stunipaddresses())

    def get_local_stunipaddresses(self):
        """
        :return: A list of v6 and v4 LOCAL StunIpAddress from StunMeasurement.
        """
        return self.stunipaddress_set.filter(ip_address_kind=StunIpAddress.Kinds.LOCAL)

    def get_local_addresses(self):
        return [r.ip_address for r in self.get_local_stunipaddresses()]

    def get_remote_stunipaddresses(self):
        return self.stunipaddress_set.filter(ip_address_kind=StunIpAddress.Kinds.REMOTE)

    def get_remote_addresses(self):
        return [r.ip_address for r in self.get_remote_stunipaddresses()]

    def get_remote_v4_addresses(self):
        return [ip for ip in self.get_remote_addresses() if "." in ip]

    def get_remote_v6_addresses(self):
        return [ip for ip in self.get_remote_addresses() if ":" in ip]

    def is_private_v4(self):

        excluded_ranges = [
            IPNetwork("10.0.0.0/8"),
            IPNetwork("172.16.0.0/12"),
            IPNetwork("192.168.0.0/16"),
            IPNetwork("127.0.0.0/8")
        ]

        for i in range(224, 256):
            excluded_ranges.append(IPNetwork("%d.0.0.0/8" % i))

        for e in excluded_ranges:
            for local in self.get_local_v4_ipaddresses():
                if IPAddress(local) in e:
                    return True

        return False

    def is_private_v6(self):

        excluded_ranges = [
            IPNetwork("2000::/3"),
            IPNetwork("2001::/32"),
            IPNetwork("2001:db8::/32"),
            IPNetwork("2002::/16"),
        ]

        for e in excluded_ranges:
            for local in self.get_local_v6_stunipaddresses():
                if IPAddress(local) in e:
                    return True

        return False

    def has_noisy_prefix(self):
        """
        :return: True if the StunMeasurement has any address in a nosiy prefix
         (prefixes not helping in the measurements)
        """

        casa_de_internet_prefixes = NOISY_PREFIXES
        nosiy_prefixes = [IPNetwork(p) for p in casa_de_internet_prefixes]

        for nosiy_prefix in nosiy_prefixes:
            for local in self.get_local_stunipaddresses():
                if IPAddress(local) in nosiy_prefix:
                    return True
        return False

    def is_natted(self, protocol=0):
        return not self.nat_free(protocol)

    def nat_free(self, protocol=0):
        """
        :param protocol: 0 | 4 | 6
        :return:
        """

        if protocol == 0:
            return len(self.get_remote_stunipaddresses()) == 0
        elif protocol == 4:
            return len(self.get_remote_v4_addresses()) == 0
        elif protocol == 6:
            return len(self.get_remote_v6_addresses()) == 0
        else:
            return False

    def is_npt(self):

        if self.nat_free() == 0:
            return False

        local_addresses = self.get_local_v6_ipaddresses()
        remote_addressess = self.get_remote_v6_addresses()
        for local in local_addresses:
            for remote in remote_addressess:
                if StunMeasurementManager.is_npt(local, remote):
                    return True
        return False

    def get_country(self):
        all_addresses = self.get_local_addresses() + self.get_remote_addresses()
        ccs = []
        for local in all_addresses:
            cc = get_cc_from_ip_address(local)
            if cc != "XX":
                ccs.append(cc)
        if len(ccs) > 0:
            return Counter(ccs).most_common()[0][0]
        else:
            return "XX"


def enum(**enums):
    return type(str("Enum"), (), enums)


class StunIpAddress(models.Model):
    """
        Place to store each IP address for that client for that measurement
    """

    Kinds = enum(LOCAL=1, REMOTE=2, NA=0)

    ip_address = models.GenericIPAddressField(default="127.0.0.1")
    ip_address_kind = models.IntegerField(default=0)
    country = models.CharField(
        max_length=3, default='DEF', help_text="Country after IP-->Country resolution"
    )

    stun_measurement = models.ForeignKey(StunMeasurement)

    def resolve_country(self, persist=True):
        cc = get_cc_from_ip_address(self.ip_address)
        if persist:
            self.country = cc
            self.save()
        return cc

    def __str__(self):
        return str(self.ip_address)


class StunIpAddressChangeEvent(models.Model):
    """
        Class that represents a change in the client's public IP address
    """
    previous = models.GenericIPAddressField(default="127.0.0.1")
    current = models.GenericIPAddressField(default="127.0.0.1")
    stun_measurement = models.ForeignKey(StunMeasurement)
