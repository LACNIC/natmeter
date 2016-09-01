from __future__ import unicode_literals
from libraries.classes import *
from django.db import models
from django.utils.timezone import now
from ipaddr import *

#
# class StunQuerySet(models.query.QuerySet):
#     def get_public_v4(self):
#         return self.filter(state='published')
#
#
# class StunMeasurementManager(models.Manager):
#     def get_query_set(self):
#         model = models.get_model('news', 'NewsItem')
#         return StunQuerySet(model)


class StunMeasurement(models.Model):
    """
        Stun measurement class. Stores the results provided
        by the JavaScript STUN/TURN software probe.
    """
    server_test_date = models.DateTimeField(default=now())
    client_test_date = models.DateTimeField(default=now())

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

    def is_private(self):
        address = IPAddress(self.cookie)
        if address.version == 4:
            return self.is_private_v4()
        else:
            return self.is_private_v6()

    def __str__(self):
        v4 = []
        v6 = []
        data = self.stunipaddress_set.all()
        for d in data:
            if ":" not in d.ip_address:
                v4.append(d)
            else:
                v6.append(d)

        final_str = ""
        if len(v4) > 0:
            v4_str = ""
            for d in v4:
                v4_str += str(d) + " "
            final_str += "%d STUN v4 candidates (%s)" % (len(v4), v4_str)
        v6_str = ""
        if len(v6) > 0:
            for d in v6:
                v6_str += str(d) + " "
            final_str += ", %d STUN v6 candidates (%s)" % (len(v6), v6_str)

        if self.cookie is not None:
            final_str += ", cookie: %s" % self.cookie

        return final_str


class StunIpAddress(models.Model):
    """
        Place to store each IP address for that client for that measurement
    """
    ip_address = models.GenericIPAddressField(default="127.0.0.1")
    stun_measurement = models.ForeignKey(StunMeasurement)

    def __str__(self):
        return str(self.ip_address)
