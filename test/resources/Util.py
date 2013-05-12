from suds.sax.date import DateTime


class Util(object):

    def xml_datetime_difference(self, start, end):
        start_dt = DateTime(start).datetime
        end_dt = DateTime(end).datetime
        return (end_dt - start_dt).total_seconds()