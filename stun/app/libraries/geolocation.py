import geoip2.database
import stun.settings as settings
from ipaddress import IPv4Address, IPv6Address


def get_cc_from_ip_address(ip_address):
    """
    Translate one IP address into a 2-digit country code (e.g.: ZA)
    :param ip_address:
    :return:
    """
    if ":" in ip_address:
        ip = IPv6Address(unicode(ip_address))
    else:
        ip = IPv4Address(unicode(ip_address))

    error = "XX"

    if not ip.is_global:
        return error

    try:
        reader = geoip2.database.Reader("%s/%s" % (settings.STATIC_ROOT, "geolocation/GeoLite2-City.mmdb"))
        cc = reader.city(ip_address).country.iso_code
    except Exception as e:
        # TODO logging
        cc = error
        print e

    if cc is None:
        cc = error

    return cc
