import base64
import re
from datetime import datetime
from robot.libraries.BuiltIn import BuiltIn
from SudsLibrary.wsse import AutoUsernameToken


class Util(object):

    def xml_datetime_difference(self, start, end=None):
        start = self._trim_to_sec(start)
        start_dt = self._iso_to_datetime(start)
        if end is None:
            end_dt = datetime.utcnow()
        else:
            end = self._trim_to_sec(end)
            end_dt = self._iso_to_datetime(end)
        return (end_dt - start_dt).total_seconds()

    def set_fixed_nonce(self, nonce):
        """`nonce` should be Base64 encoded."""
        token = self._get_autousernametoken()
        token.autosetnonce = False
        token.setnonce(base64.decodestring(nonce))

    def set_fixed_created(self, created):
        """Set a fixed value for the created element.

        Only supports ISO format with UTC zone, with precision to seconds, e.g. 2014-09-20T17:46:40Z
        """
        dt = self._iso_to_datetime(created)
        token = self._get_autousernametoken()
        token.autosetcreated = False
        token.setcreated(dt)

    def _iso_to_datetime(self, dt):
        """

        :type dt: str, unicode
        """
        pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z'
        if not isinstance(dt, (str, unicode)) or not re.match(pattern, dt):
            raise ValueError("created must be a string and match %s" % pattern)
        return datetime.strptime(dt, '%Y-%m-%dT%H:%M:%SZ')

    def _trim_to_sec(self, dt):
        return dt[:19] + 'Z'

    def _get_autousernametoken(self):
        sl = BuiltIn().get_library_instance('SudsLibrary')
        wsse = sl._get_wsse(False)
        return [token for token in wsse.tokens if isinstance(token, AutoUsernameToken)][0]
