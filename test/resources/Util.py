from suds.sax.date import UTC
from datetime import datetime


class Util(object):

    def xml_datetime_difference(self, start, end=None):
        start_dt = UTC(start).datetime
        if end is None:
            # prevent adjustment for timezones due to daylight savings time
            end_dt = UTC(str(UTC())).datetime
        else:
            end_dt = UTC(end).datetime
        return (end_dt - start_dt).total_seconds()