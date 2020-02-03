from __future__ import unicode_literals
import operator
from django.db.models import Q, Count
from app.libraries.geolocation import get_cc_from_ip_address
from collections import Counter, defaultdict
from django.db import models, transaction
from django.utils.timezone import now
from libraries.classes import *
from ipaddr import *
from static_defs import NOISY_PREFIXES
from tqdm import tqdm
from django.db.models import Avg, Max
from stun import settings
import requests
import pytz
import json
from django.db.models import Count
from django.db.transaction import commit_on_success


class StunMeasurementManager(models.Manager):
    def get_average(self, _list=[]):
        return 1.0 * sum(_list) / len(_list)

    def get_max(self, _list=[]):
        return max(_list)

    def get_results(self, consider_country=False, since=None, until=None):  # everythin in the last 60 days
        """
        :param consider_country:
        :param window: time window going backwards. 0 means infinity (all data)
        :return: Get clean results ready for doing stats
        """
        stun_measurements = StunMeasurement.objects.annotate(
            ips=Count('stunipaddress'),
            local_ips=Count('stunipaddress', filter=Q(stunipaddress__ip_address_kind=StunIpAddress.Kinds.LOCAL)),
            remote_ips=Count('stunipaddress', filter=Q(stunipaddress__ip_address_kind=StunIpAddress.Kinds.REMOTE)),
            dotlocal_ips=Count('stunipaddress', filter=Q(stunipaddress__ip_address_kind=StunIpAddress.Kinds.DOTLOCAL)),
        ).filter(
            noisy_prefix=False,
        ).exclude(
            stunipaddress__ip_address_kind=StunIpAddress.Kinds.DOTLOCAL
        )
        if consider_country:
            stun_measurements = stun_measurements.filter(stunipaddress__country__in=settings.all_ccs)

        if since:
            stun_measurements = stun_measurements.filter(server_test_date__gte=since)

        if until:
            stun_measurements = stun_measurements.filter(server_test_date__lte=until)

        return stun_measurements

    def get_v6_results(self, consider_country=False, since=None, until=None):
        """
        :return: All StunMeasurements that have shown IPv6 support
        """
        return self.get_results(consider_country=consider_country, since=since, until=until).filter(v6_count__gt=0)

    def get_v4_results(self, consider_country=False, since=None, until=None):
        """
        :return: All StunMeasurements that have shown IPv4 support
        """
        return self.get_results(consider_country=consider_country, since=since, until=until).filter(v4_count__gt=0)

    def get_dualstack_results(self, consider_country=False, since=None, until=None):
        """
        :return: All StunMeasurements that have shown IPv4 and IPv6 support
        """
        return StunMeasurement.objects.get_results(consider_country=consider_country, since=since, until=until).filter(dualstack=True)

    def get_dualstack_percentage(self, consider_country=False, since=None, until=None):
        ds = StunMeasurement.objects.get_dualstack_results(consider_country=consider_country, since=since, until=until).count()
        return 100.0 * ds / StunMeasurement.objects.get_results(consider_country=consider_country, since=since, until=until).count()

    def v6_count(self, since=None, until=None):
        """
        :return: All v6_counts (# of addresses) for StunMeasurements that have shown IPv6 support
        """
        return StunMeasurement.objects.get_v6_results(since=since, until=until).values_list('v6_count', flat=True)

    def v6_count_avg(self, since=None, until=None):
        return StunMeasurement.objects.get_v6_results(since=since, until=until).aggregate(Avg('v6_count'))['v6_count__avg']

    def v6_count_max(self, since=None, until=None):
        return StunMeasurement.objects.get_v6_results(since=since, until=until).aggregate(Max('v6_count'))['v6_count__max']

    def v4_count(self, since=None, until=None):
        """
        :return: All v4_counts (# of addresses) for StunMeasurements that have shown IPv4 support
        """
        return StunMeasurement.objects.get_v4_results(since=since, until=until).values_list('v4_count', flat=True)

    def v4_count_avg(self, since=None, until=None):
        return StunMeasurement.objects.get_v4_results(since=since, until=until).aggregate(Avg('v4_count'))['v4_count__avg']

    def v4_count_max(self, since=None, until=None):
        return StunMeasurement.objects.get_v4_results(since=since, until=until).aggregate(Max('v4_count'))['v4_count__max']

    def get_v6_nat_percentage(self, consider_country=False, since=None, until=None):
        """
        :return: NAT % (percentage) for NAT 66
        """

        from app.caching.caching import cache as custom_cache
        from management.commands.set_caches import get_announcements
        announcements = custom_cache.get_or_set(
            custom_cache.keys.announcements,
            call=get_announcements
        )

        v6_stunmeasurements = self.get_v6_results(consider_country=consider_country, since=since, until=until)

        # weigh by country
        total_region_ips = 0
        total_region_natted_ips = 0
        ccs = settings.all_ccs
        for cc in ccs:  # TODO only lac announcements
            cc_msms = v6_stunmeasurements
            cc_msms_natted = cc_msms.filter(nat_free_6=False)

            if len(cc_msms_natted) == 0:
                continue

            adv = int(announcements[cc])  # announced prefixes
            cc_natted_ratio = 1.0 * len(cc_msms_natted) / len(cc_msms)
            adv_natted_ips = adv * cc_natted_ratio
            total_region_ips += adv
            total_region_natted_ips += adv_natted_ips

        return 100.0 * total_region_natted_ips / total_region_ips if total_region_ips > 0 else 0

    def get_v4_nat_percentage(self, consider_country=False, since=None, until=None):
        """
        :return: NAT % (percentage) for NAT 44
        """

        from app.caching.caching import cache as custom_cache
        from app.management.commands.set_caches import get_announcements
        announcements = custom_cache.get_or_set(
            custom_cache.keys.announcements,
            call=get_announcements
        )

        v4_stunmeasurements = self.get_v4_results(consider_country=consider_country, since=since, until=until)

        # weigh by country
        total_region_ips = 0
        total_region_natted_ips = 0
        ccs = settings.all_ccs  # list(set([s.get_country() for s in v4]))  # unique countries only
        for cc in ccs:  # TODO only lac announcements
            cc_msms = v4_stunmeasurements.filter(stunipaddress__country=cc)
            cc_msms_natted = cc_msms.filter(nat_free_4=False)

            if len(cc_msms_natted) == 0:
                continue

            adv = int(announcements[cc])  # announced prefixes
            cc_natted_ratio = 1.0 * len(cc_msms_natted) / len(cc_msms)
            adv_natted_ips = adv * cc_natted_ratio
            total_region_ips += adv
            total_region_natted_ips += adv_natted_ips

        return 100.0 * total_region_natted_ips / total_region_ips if total_region_ips > 0 else 0

    def nat_0_percentage(self, consider_country=False, since=None, until=None):
        """
        :return: NAT % (percentage) for any kind of NAT
        """
        natted = StunMeasurement.objects.get_results(consider_country=consider_country, since=since, until=until).filter(nat_free_0=False).count()
        return 100.0 * natted / StunMeasurement.objects.get_results(consider_country=consider_country, since=since, until=until).count()

    def nat_4_percentage(self, consider_country=False, since=None, until=None):
        """
        :return: NAT % (percentage) for NAT 44
        """
        natted = StunMeasurement.objects.get_results(consider_country=consider_country, since=since, until=until).filter(nat_free_4=False).count()
        return 100.0 * natted / StunMeasurement.objects.get_results(consider_country=consider_country, since=since, until=until).count()

    def nat_6_percentage(self, consider_country=False, since=None, until=None):
        """
        :return: NAT % (percentage) for NAT 66
        """
        results = StunMeasurement.objects.get_results(
            consider_country=consider_country,
        ).filter(
            v6_count__gt=0
        )

        if since:
            results = results.filter(server_test_date__gte=since)

        if until:
            results = results.filter(server_test_date__lte=until)

        natted = results.filter(
            nat_free_6=False
        )

        return 100.0 * natted.count() / results.count()

    def v6_only_percentage(self, consider_country=False, since=None, until=None):
        v6_only = StunMeasurement.objects.get_v6_results(consider_country=consider_country, since=since, until=until).filter(v4_count=0).count()
        return 100.0*v6_only / StunMeasurement.objects.get_v6_results(consider_country=consider_country, since=since, until=until).count()

    def get_v6_hosts_with_v4_capability_percentage(self, consider_country=False, since=None, until=None):
        """
        :return: v4 capability % (percentage) for v6-only hosts
        """
        v6 = self.get_v6_results(consider_country=consider_country, since=since, until=until)
        is_v4_capable = [s for s in v6 if s.is_v6_with_v4_capabilities()]
        return 100.0 * len(is_v4_capable) / len(v6)

    def get_npt_percentage(self, consider_country=False, since=None, until=None):
        """
        :return: NPT % (percentage) among v6-only hosts
        """
        is_npt = self.get_v6_results(consider_country=consider_country, since=since, until=until).filter(npt=True).count()
        return 100.0 * is_npt / self.get_v6_results(consider_country=consider_country, since=since, until=until).count()


    def get_nat64_percentage(self, consider_country=False, since=None, until=None):
        """
        :return: NAT64 % (percentage) among v6-only hosts
        """
        is_nat64 = self.get_v6_results(consider_country=consider_country, since=since, until=until).filter(nat64=True).count()
        return 100.0 * is_nat64 / self.get_results(consider_country=consider_country, since=since, until=until, nat_free_0=False).count()

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

        if 'DEF' in counter.keys():
            counter.pop('DEF')
        if 'XX' in counter.keys():
            counter.pop('XX')

        return counter

    def get_private_pfx_counter_v6(self):

        results = self.get_v6_results()
        pvt_pfxs = []
        for r in results:
            addresses = r.get_local_v6_ipaddresses()
            world = StunMeasurement.objects.show_addresses_to_the_world(addresses)
            pvt_pfxs += world
        counter = Counter(pvt_pfxs).items()
        return sorted(counter, key=operator.itemgetter(1), reverse=True)

    def get_private_pfx_counter_v4(self):

        results = self.get_v4_results()
        pvt_pfxs = []
        for r in results:
            addresses = r.get_local_v4_ipaddresses()
            world = StunMeasurement.objects.show_addresses_to_the_world(addresses)
            pvt_pfxs += world
        counter = Counter(pvt_pfxs).items()
        return sorted(counter, key=operator.itemgetter(1), reverse=True)

    def get_public_pfxs_nat_free_4_false(self, since=None, until=None):
        return self._get_public_pfxs_nat_free_generic({'nat_free_4': False, 'v4_count__gt':0 }, since=since, until=until)

    def get_public_pfxs_nat_free_4_true(self, since=None, until=None):
        return self._get_public_pfxs_nat_free_generic({'nat_free_4': True, 'v4_count__gt':0 }, since=since, until=until)

    def get_public_pfxs_nat_free_0_false(self, since=None, until=None):
        return self._get_public_pfxs_nat_free_generic({'nat_free_0': False }, since=since, until=until)

    def get_public_pfxs_nat_free_0_true(self, since=None, until=None):
        return self._get_public_pfxs_nat_free_generic({'nat_free_0':True }, since=since, until=until)

    def _get_public_pfxs_nat_free_generic(self, *args, **kwargs):

        ips = StunMeasurement.objects.get_results(since=kwargs['since'], until=kwargs['until']).filter(Q(**args[0])).filter(
            stunipaddress__ip_address_kind=StunIpAddress.Kinds.REMOTE
        ).values(
            'pk'
        ).values_list(
            'stunipaddress__ip_address', flat=True
        )

        return set(StunMeasurementManager.show_addresses_to_the_world(ips))

    def public_pfxs_nat_0_false_percentage(self, since=None, until=None):
        natted = StunMeasurement.objects.get_public_pfxs_nat_free_0_false(since=since, until=until)
        nat_free = StunMeasurement.objects.get_public_pfxs_nat_free_0_true(since=since, until=until)

        return 100.0*len(natted) / (len(natted) + len(nat_free))

    @commit_on_success
    def set_attributes(self, persist=True, force=True):

        self_filter = self.all()
        if not force:
            self_filter = self.filter(already_processed=False)

        for sm in tqdm(self_filter):
            sm.set_attributes(persist=persist, force=force)

    def resolve_announcing_asns(self):

        session = requests.Session()

        sms = self.annotate(
            count=Count('stunipaddress__announcingasn')
        ).filter(
            count=0
        )

        for sm in tqdm(sms):
            sm.resolve_announcing_asns(session=session)

        session.close()



    @staticmethod
    def is_npt(ip1, ip2):

        try:
            v6_1 = IPv6Address(ip1)
            v6_2 = IPv6Address(ip2)
        except AddressValueError:
            return False

        return v6_1.exploded.split(":")[4:] == v6_2.exploded.split(":")[4:] and v6_1.exploded.split(":")[:4] != v6_2.exploded.split(":")[:4]

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

    @classmethod
    def is_private(cls, address):
        return cls.is_private_v4(address) or cls.is_private_v6(address)

    @classmethod
    def is_private_v4(cls, address):

        excluded_ranges = [
            IPNetwork("10.0.0.0/8"),
            IPNetwork("172.16.0.0/12"),
            IPNetwork("192.168.0.0/16"),
            IPNetwork("127.0.0.0/8")
        ]

        for i in range(224, 256):
            excluded_ranges.append(IPNetwork("%d.0.0.0/8" % i))

        for e in excluded_ranges:
            if IPAddress(address) in e:
                return True

        return False

    @classmethod
    def is_private_v6(cls, address):

        excluded_ranges = [
            IPNetwork("2000::/3"),
            IPNetwork("2001::/32"),
            IPNetwork("2001:db8::/32"),
            IPNetwork("2002::/16"),
        ]

        for e in excluded_ranges:
            if IPAddress(address) in e:
                return True

        return False


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

    nat_free_0 = models.NullBooleanField(default=None, null=True, help_text="Any kind of NAT")
    nat_free_4 = models.NullBooleanField(default=None, null=True, help_text="NAT")
    nat_free_6 = models.NullBooleanField(default=None, null=True)

    dualstack = models.NullBooleanField(default=None, null=True, help_text="Dualstack detected")

    v6_only = models.NullBooleanField(default=None, null=True, help_text="v6 only host")
    v4_only = models.NullBooleanField(default=None, null=True, help_text="v4 only host")

    v4_count = models.IntegerField(default=0, null=True, help_text="IPv4 addresses count for that host")
    v6_count = models.IntegerField(default=0, null=True, help_text="IPv6 addresses count for that host")

    npt = models.NullBooleanField(default=None, null=True, help_text="Usage of NPT")

    nat64 = models.NullBooleanField(default=None, null=True, help_text="Usage of NAT64")

    noisy_prefix = models.NullBooleanField(default=None, null=True, help_text="This measurement comes from one of the ignored prefixes (special cases)")

    href = models.CharField(default=None, null=True, help_text="Site providing the results", max_length=1024)

    user_agent = models.CharField(default=None, null=True, help_text="User Agent", max_length=1024)

    already_processed = models.BooleanField(default=False)

    n_addr_local = models.IntegerField(default=-1)
    n_addr_remote = models.IntegerField(default=-1)
    n_addr_dotlocal = models.IntegerField(default=-1)

    objects = StunMeasurementManager()

    def set_attributes(self, persist=True, force=True, session=None):
        """Attributes to make post-processing, filter, etc. easier and quicker
        :param force: Overwrite existing value in DB
        :return: None
        """

        # save object in the end
        self.set_nat_free(persist=persist, force=force)
        self.set_dualstack(persist=persist, force=force)
        self.v6_only = self.is_v6_only()
        self.v4_only = self.is_v4_only()
        self.v6_count = self.get_v6_count()
        self.v4_count = self.get_v4_count()
        self.npt = self.is_npt()
        self.nat64 = self.is_nat64()
        self.noisy_prefix = self.has_noisy_prefix()  # TODO provate prefixes
        self.already_processed = True

        self.n_addr_local, self.n_addr_remote, self.n_addr_dotlocal = self.get_ip_count()

        self.save()

    def is_v6_only(self):
        """
        :return: True if this host had v6-only interfaces during this STUN measurement. False otherwise.
        """
        local_addresses = self.get_local_addresses()
        for ip in local_addresses:
            if "." in ip:
                return False
        return True

    def is_v4_only(self):
        """
        :return: True if this host had v6-only interfaces during this STUN measurement. False otherwise.
        """
        local_addresses = self.get_local_addresses()
        for ip in local_addresses:
            if ":" in ip:
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

    def get_v6_count(self, force=False):
        return len(self.get_local_v6_stunipaddresses())

    def get_local_v4_stunipaddresses(self):
        """
        :return: A list of v4 LOCAL StunIpAddress from StunMeasurement.
        """
        ips = self.stunipaddress_set.filter(ip_address_kind=StunIpAddress.Kinds.LOCAL)
        v4 = [ip for ip in ips if "." in ip.ip_address]
        return v4

    def get_v4_count(self, force=False):
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

    def get_asns(self):
        return [asn.asn for asn in AnnouncingAsn.objects.filter(ip_address__stun_measurement=self)]

    def get_remote_v4_addresses(self):
        return [ip for ip in self.get_remote_addresses() if "." in ip]

    def get_remote_v6_addresses(self):
        return [ip for ip in self.get_remote_addresses() if ":" in ip]

    def is_private_v4(self):
        return any([StunMeasurementManager.is_private_v4(local) for local in self.get_local_v4_stunipaddresses()])

    def is_private_v6(self):
        return any([StunMeasurementManager.is_private_v6(local) for local in self.get_local_v6_stunipaddresses()])

    def is_private(self):
        return self.is_private_v4() or self.is_private_v6()

    def has_noisy_prefix(self, force=False):
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

    def set_dualstack(self, persist=True, force=False):
        if force or not self.dualstack:
            self.dualstack = self.get_v4_count() > 0 and self.get_v6_count() > 0

        if persist:
            self.save()

    def is_natted(self):
        """
        :return: True if StunMeasurement has *some* kind of NAT
        """
        return not self.nat_free_0

    def set_nat_free(self, persist=True, force=False):

        if force or not self.nat_free_0:
            self.nat_free_0 = self.nat_free(0)
        if force or not self.nat_free_4:
            self.nat_free_4 = self.nat_free(4)
        if force or not self.nat_free_6:
            self.nat_free_6 = self.nat_free(6)

        if persist:
            self.save()

    def nat_free(self, protocol=0):
        """
        :param protocol: 0 | 4 | 6
        :return:    protocol=={ 4|6 } True if StunMeasurement has no NAT for that protocol
                    protocol==0 True if StunMeasurement has no NAT of any kind
        """

        if protocol == 0:
            return len(self.get_remote_stunipaddresses()) == 0 and len(self.get_local_stunipaddresses()) > 0
        elif protocol == 4:
            return len(self.get_remote_v4_addresses()) == 0 and len(self.get_local_v4_ipaddresses()) > 0
        elif protocol == 6:
            return len(self.get_remote_v6_addresses()) == 0 and len(self.get_local_v6_ipaddresses()) > 0
        else:
            return False

    def is_npt(self):

        local_addresses = self.get_local_v6_ipaddresses()
        remote_addressess = self.get_remote_v6_addresses()
        for local in local_addresses:
            for remote in remote_addressess:
                if StunMeasurementManager.is_npt(local, remote):
                    return True
        return False

    def is_nat64(self):
        return all([':' in ip for ip in self.get_local_v6_ipaddresses()]) and self.get_remote_v4_addresses() and self.get_remote_v6_addresses()

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

    def resolve_announcing_asns(self, session=None):

        local_session = False
        if not session:
            session = requests.Session()
            local_session = True

        ips = self.stunipaddress_set.all()
        ips = [ip for ip in ips if not StunMeasurementManager.is_private(ip)]
        for ip in ips:
            ip.resolve_announcing_asns(session=session)

        if local_session:
            session.close()

    def get_asn(self):

        _set = AnnouncingAsn.objects.filter(ip_address__stun_measurement=self)

        return ','.join([str(asn.asn) for asn in _set])

    def get_ip_count(self):

        local = self.stunipaddress_set.filter(ip_address_kind=StunIpAddress.Kinds.LOCAL).count()
        remote = self.stunipaddress_set.filter(ip_address_kind=StunIpAddress.Kinds.REMOTE).count()
        dotlocal = self.stunipaddress_set.filter(ip_address_kind=StunIpAddress.Kinds.DOTLOCAL).count()

        return local, remote, dotlocal


def enum(**enums):
    return type(str("Enum"), (), enums)


class StunIpAddress(models.Model):
    """
        Place to store each IP address for that client for that measurement
    """

    Kinds = enum(LOCAL=1, REMOTE=2, DOTLOCAL=3, NA=0)

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

    def resolve_announcing_asns(self, session=None):

        local_session = False
        if not session:
            session = requests.Session()
            local_session = True

        if StunMeasurementManager.is_private(self.ip_address):
            return

        epoch = datetime(1970, 1, 1, tzinfo=pytz.UTC)
        date = self.stun_measurement.server_test_date.astimezone(pytz.UTC)
        diff = date - epoch
        starttime = int(diff.total_seconds())

        respose = session.get(
            "https://stat.ripe.net/data/routing-history/data.json?"
            "resource={pfx}&"
            "starttime={starttime}&"
            "endtime={endtime}".format(
                pfx=StunMeasurementManager.show_address_to_the_world(self.ip_address) + '/24',
                starttime=starttime,
                endtime=starttime+86400
            )
        )

        if local_session:
            session.close()

        json_response = json.loads(respose.text)

        if "data" in json_response.keys() and "by_origin" in json_response["data"].keys():
            origins = json_response["data"]["by_origin"]
            for origin in origins:
                asn = int(origin["origin"])
                AnnouncingAsn.objects.create(
                    ip_address=self,
                    asn=asn
                )

    def __str__(self):
        return str(self.ip_address)

class AnnouncingAsn(models.Model):
    asn = models.IntegerField(default=0, null=True)
    ip_address = models.ForeignKey(StunIpAddress)


class StunIpAddressChangeEvent(models.Model):
    """
        Class that represents a change in the client's public IP address
    """
    previous = models.GenericIPAddressField(default="127.0.0.1")
    current = models.GenericIPAddressField(default="127.0.0.1")
    stun_measurement = models.ForeignKey(StunMeasurement)


class Report(models.Model):

    date = models.DateTimeField(default=datetime_uy)
    window = models.IntegerField(default=90, help_text="Time window this report covers (start=now-window)")

    v6_avg = models.FloatField()
    v4_avg = models.FloatField()
    v6_max = models.FloatField()
    v4_max = models.FloatField()

    all_nat = models.FloatField()
    all_nat_world = models.FloatField()

    v4_nat = models.FloatField()
    v4_nat_world = models.FloatField()
    # cache.v4_nat = StunMeasurement.objects.get_v4_nat_percentage(consider_country=True)
    # cache.v4_nat_world = StunMeasurement.objects.get_v4_nat_percentage(consider_country=False)

    v6_nat = models.FloatField()
    v6_nat_world = models.FloatField()

    v6_only = models.FloatField()
    v6_only_world = models.FloatField(default=-1)

    v6_with_v4_capacity = models.FloatField()
    v6_with_v4_capacity_world = models.FloatField()

    dualstack = models.FloatField()
    dualstack_world = models.FloatField()

    npt = models.FloatField()
    npt_world = models.FloatField()

    nat64 = models.FloatField(default=-1)
    nat64_world = models.FloatField(default=-1)

    public_pfxs_nat_free_0_false_percentage = models.FloatField()

    # announcements = get_announcements())

    # country_participation = StunMeasurement.objects.get_country_participation()
    # v6_private_prefixes = StunMeasurement.objects.get_private_pfx_counter_v6()
    # v4_private_prefixes = StunMeasurement.objects.get_private_pfx_counter_v4()

    def set_values(self):

        now = datetime_uy().now()
        since = now - timedelta(days=self.window)

        with tqdm(total=18) as pbar:
            self.v6_avg = StunMeasurement.objects.v6_count_avg(since=since)
            self.v4_avg = StunMeasurement.objects.v4_count_avg(since=since)
            self.v6_max = StunMeasurement.objects.v6_count_max(since=since)
            self.v4_max = StunMeasurement.objects.v4_count_max(since=since)
            pbar.update(4)

            self.all_nat = StunMeasurement.objects.nat_0_percentage(consider_country=True, since=since)
            self.all_nat_world = StunMeasurement.objects.nat_0_percentage(consider_country=False, since=since)
            pbar.update(2)

            self.v4_nat = StunMeasurement.objects.nat_4_percentage(consider_country=True, since=since)
            self.v4_nat_world = StunMeasurement.objects.nat_4_percentage(consider_country=False, since=since)
            # cache.v4_nat = StunMeasurement.objects.get_v4_nat_percentage(consider_country=True)
            # cache.v4_nat_world = StunMeasurement.objects.get_v4_nat_percentage(consider_country=False)
            pbar.update(2)

            self.v6_nat = StunMeasurement.objects.nat_6_percentage(consider_country=True, since=since)
            self.v6_nat_world = StunMeasurement.objects.nat_6_percentage(consider_country=False, since=since)
            pbar.update(2)

            self.v6_only = StunMeasurement.objects.v6_only_percentage(consider_country=True, since=since)
            self.v6_only_world = StunMeasurement.objects.v6_only_percentage(consider_country=False, since=since)
            pbar.update(1)

            self.v6_with_v4_capacity = StunMeasurement.objects.get_v6_hosts_with_v4_capability_percentage(consider_country=True, since=since)
            self.v6_with_v4_capacity_world = StunMeasurement.objects.get_v6_hosts_with_v4_capability_percentage(consider_country=False, since=since)
            pbar.update(2)

            self.dualstack = StunMeasurement.objects.get_dualstack_percentage(consider_country=True, since=since)
            self.dualstack_world = StunMeasurement.objects.get_dualstack_percentage(consider_country=False, since=since)
            pbar.update(2)

            self.npt = StunMeasurement.objects.get_npt_percentage(consider_country=True, since=since)
            self.npt_world = StunMeasurement.objects.get_npt_percentage(consider_country=False, since=since)
            pbar.update(1)

            self.nat64 = StunMeasurement.objects.get_npt_percentage(consider_country=True, since=since)
            self.nat64_world = StunMeasurement.objects.get_npt_percentage(consider_country=False, since=since)
            pbar.update(1)



            self.public_pfxs_nat_free_0_false_percentage = StunMeasurement.objects.public_pfxs_nat_0_false_percentage(since=since)
            pbar.update(1)


            # announcements = get_announcements())

            # self.country_participation = StunMeasurement.objects.get_country_participation()
            # self.v6_private_prefixes = StunMeasurement.objects.get_private_pfx_counter_v6()
            # self.v4_private_prefixes = StunMeasurement.objects.get_private_pfx_counter_v4()