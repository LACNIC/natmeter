from datetime import tzinfo, timedelta, datetime


class GMTUY(tzinfo):
    """
        Auxuliary class providing time zone information
    """

    def utcoffset(self, dt):
        return timedelta(hours=-3)

    def tzname(self, dt):
        return "GMT -3: Uruguay"

    def dst(self, dt):
        return timedelta(0)


def datetime_uy():
    return datetime.now(tz=GMTUY())
