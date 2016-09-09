from __future__ import unicode_literals
from libraries.classes import *
from django.db import models
from django.utils.timezone import now
from ipaddr import *


class StunMeasurementManager(models.Manager):
    @staticmethod
    def is_npt(ip1, ip2):

        try:
            v6_1 = IPv6Address(ip1)
            v6_2 = IPv6Address(ip2)
        except AddressValueError:
            return False

        return v6_1.exploded.split(":")[4:] == v6_2.exploded.split(":")[4:]


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
        ips = self.stunipaddress_set.all()
        for ip in ips:
            if "." in ip.ip_address:
                return False
        return True

    def is_private_v4(self):

        cookie = self.cookie

        excluded_ranges = [
            IPNetwork("10.0.0.0/8"),
            IPNetwork("172.16.0.0/12"),
            IPNetwork("192.168.0.0/16"),
            IPNetwork("127.0.0.0/8")
        ]

        for i in range(224, 256):
            excluded_ranges.append(IPNetwork("%d.0.0.0/8" % i))

        for e in excluded_ranges:
            if IPAddress(cookie) in e:
                return False

        return True

    def is_private_v6(self):

        cookie = self.cookie

        excluded_ranges = [
            IPNetwork("2000::/3"),
            IPNetwork("2001::/32"),
            IPNetwork("2001:db8::/32"),
            IPNetwork("2002::/16"),
        ]

        for e in excluded_ranges:
            if IPAddress(cookie) in e:
                return False

        return True

    def is_natted(self):

        public_addresses = self.stunipaddress_set.filter(ip_address_kind=StunIpAddress.Kinds.PUBLIC)
        private_addresses = self.stunipaddress_set.filter(ip_address_kind=StunIpAddress.Kinds.PRIVATE)

        if len(public_addresses) <= len(private_addresses):
            return False

        return True

    def nat_free(self):
        return not self.is_natted()


def enum(**enums):
    return type(str("Enum"), (), enums)


class StunIpAddress(models.Model):
    """
        Place to store each IP address for that client for that measurement
    """

    Kinds = enum(PRIVATE=1, PUBLIC=2, NA=0)

    ip_address = models.GenericIPAddressField(default="127.0.0.1")
    ip_address_kind = models.IntegerField(default=0)

    stun_measurement = models.ForeignKey(StunMeasurement)

    def __str__(self):
        return str(self.ip_address)


class StunIpAddressChangeEvent(models.Model):
    """
        Class that represents a change in the client's public IP address
    """
    previous = models.GenericIPAddressField(default="127.0.0.1")
    current = models.GenericIPAddressField(default="127.0.0.1")
    stun_measurement = models.ForeignKey(StunMeasurement)
