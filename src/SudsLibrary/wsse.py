# Copyright 2013 Kevin Ormbrek
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from suds.wsse import Security
from suds.wsse import Timestamp
import robot


class AutoTimestamp(Timestamp):

    def __init__(self, validity=90):
        Timestamp.__init__(self, validity)
        self.validity = validity

    def xml(self):
        Timestamp.__init__(self, self.validity)
        return Timestamp.xml(self)


class _WsseKeywords(object):

    def apply_security_timestamp(self, duration='90 seconds'):
        """Applies a timestamp element to future requests valid for the given `duration`.

        The SOAP header will contain a Timestamp element as specified in the
        WS-Security extension. The Created and Expires values are updated
        every time a request is made.

        `duration` must be given in Robot Framework's time format (e.g.
        '1 minute', '2 min 3 s', '4.5').
        """
        validity = robot.utils.timestr_to_secs(duration)
        wsse = self._get_wsse()
        wsse.tokens = [x for x in wsse.tokens if not isinstance(x, Timestamp)]
        wsse.tokens.insert(0, AutoTimestamp(validity))
        self._client().options.wsse = wsse

    # private

    def _get_wsse(self, create=True):
        wsse = self._client().options.wsse
        if wsse is None and create:
            wsse = Security()
        return wsse
