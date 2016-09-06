from __future__ import unicode_literals
from libraries.classes import *
from django.db import models
from django.utils.timezone import now
from ipaddr import *


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

    def nat_free(self):
        address_wimi = self.cookie
        stun_address_set = self.stunipaddress_set.all()
        if address_wimi in stun_address_set:
            return True
        return False

    def is_natted(self):
        return not self.nat_free()

        # def __str__(self):
        #     v4 = []
        #     v6 = []
        #     data = self.stunipaddress_set.all()
        #     for d in data:
        #         if ":" not in d.ip_address:
        #             v4.append(d)
        #         else:
        #             v6.append(d)
        #
        #     v6_capable = len(v6) > 0


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
