import geoip2.database
import settings


def get_cc_from_ip_address(ip_address):
    """
    Translate one IP address into a 2-digit country code (e.g.: ZA)
    :param ip_address:
    :return:
    """
    error = "XX"
    try:
        reader = geoip2.database.Reader("%s/%s" % (settings.STATIC_ROOT, "geolocation/GeoLite2-City.mmdb"))
        cc = reader.city(ip_address).country.iso_code
    except Exception as e:
        # TODO logging
        cc = error

    return cc
