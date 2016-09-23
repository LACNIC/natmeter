from django.test import TestCase
from app.models import *


class ExternalLibraresTest(TestCase):
    def test_expansion(self):
        ip1 = "2001:db8::1"
        ip2 = "2001:0db8:0000:0000:0000:0000:0000:0001"
        self.assertEqual(IPv6Address(ip1).exploded, ip2)


class NptTest(TestCase):
    def test_identity(self):
        ip1 = "2001:13c7:7001:7000:f19c:6c05:a546:f373"
        is_npt = StunMeasurementManager.is_npt(ip1, ip1)
        self.assertTrue(is_npt)


class NatTest(TestCase):
    def test_nat(self):
        msm = StunMeasurement()
        msm.save()

        # STUN server addresses
        StunIpAddress(
            ip_address="2001:db8::3",
            ip_address_kind=StunIpAddress.Kinds.REMOTE,
            stun_measurement=msm
        ).save()
        StunIpAddress(
            ip_address="2001:db8::1",
            ip_address_kind=StunIpAddress.Kinds.REMOTE,
            stun_measurement=msm
        ).save()
        StunIpAddress(
            ip_address="2001:db8::1",
            ip_address_kind=StunIpAddress.Kinds.REMOTE,
            stun_measurement=msm
        ).save()
        StunIpAddress(
            ip_address="192.168.5.30",
            ip_address_kind=StunIpAddress.Kinds.REMOTE,
            stun_measurement=msm
        ).save()
        StunIpAddress(
            ip_address="200.47.79.5",
            ip_address_kind=StunIpAddress.Kinds.REMOTE,
            stun_measurement=msm
        ).save()
        StunIpAddress(
            ip_address="2800:26:32::abcd:ad12",
            ip_address_kind=StunIpAddress.Kinds.REMOTE,
            stun_measurement=msm
        ).save()

        # Host-only known discovered addresses
        StunIpAddress(
            ip_address="2001:db8::3",
            ip_address_kind=StunIpAddress.Kinds.LOCAL,
            stun_measurement=msm
        ).save()
        StunIpAddress(
            ip_address="2001:db8::1",
            ip_address_kind=StunIpAddress.Kinds.LOCAL,
            stun_measurement=msm
        ).save()
        StunIpAddress(
            ip_address="2001:db8::1",
            ip_address_kind=StunIpAddress.Kinds.LOCAL,
            stun_measurement=msm
        ).save()
        StunIpAddress(
            ip_address="192.168.5.30",
            ip_address_kind=StunIpAddress.Kinds.LOCAL,
            stun_measurement=msm
        ).save()

        self.assertTrue(msm.is_natted())
