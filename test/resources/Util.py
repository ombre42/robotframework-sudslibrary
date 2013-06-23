from suds.sax.date import UTC, DateTime, Timezone
import base64
from robot.libraries.BuiltIn import BuiltIn
from SudsLibrary.wsse import AutoUsernameToken


class Util(object):

    def xml_datetime_difference(self, start, end=None):
        start_dt = UTC(start).datetime
        if end is None:
            # prevent adjustment for timezones due to daylight savings time
            end_dt = UTC(str(UTC())).datetime
        else:
            end_dt = UTC(end).datetime
        return (end_dt - start_dt).total_seconds()

    def set_fixed_nonce(self, nonce):
        """`nonce` should be Base64 encoded."""
        token = self._get_autousernametoken()
        token.autosetnonce = False
        token.setnonce(base64.decodestring(nonce))

    def set_fixed_created(self, created):
        if not isinstance(created, basestring) or created[-1].upper() != 'Z':
            raise ValueError("only UTC xsd:datetime as string supported")
        token = self._get_autousernametoken()
        token.autosetcreated = False
        # get the local adjustment
        tz_parts = Timezone.split(str(DateTime(str(UTC()))))
        if len(tz_parts) == 2:
            created = created[:-1] + tz_parts[1]
        token.setcreated(created)

    def _get_autousernametoken(self):
        sl = BuiltIn().get_library_instance('SudsLibrary')
        wsse = sl._get_wsse(False)
        return [token for token in wsse.tokens if isinstance(token, AutoUsernameToken)][0]
