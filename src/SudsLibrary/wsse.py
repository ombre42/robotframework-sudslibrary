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

from .utils import *
from suds.wsse import Security
from suds.wsse import Timestamp
from suds.wsse import UsernameToken
from suds.sax.element import Element
from suds.sax.date import UTC
from random import random
from hashlib import sha1
import robot


PASSWORDTEXT_TYPE = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText'
BASE64_ENC_TYPE = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary"
WSSENS = \
    ('wsse',
     'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd')
WSUNS = \
    ('wsu',
     'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd')


class AutoTimestamp(Timestamp):

    def __init__(self, validity=90):
        Timestamp.__init__(self, validity)
        self.validity = validity

    def xml(self):
        Timestamp.__init__(self, self.validity)
        return Timestamp.xml(self)


class AutoUsernameToken(UsernameToken):

    def __init__(self, username=None, password=None, setcreated=False,
                 setnonce=False, digest=False):
        if digest:
            raise NotImplementedError()
        UsernameToken.__init__(self, username, password)
        self.autosetcreated = setcreated
        self.autosetnonce = setnonce

    def setnonce(self, text=None):
        if text is None:
            hash = sha1()
            hash.update(str(random()))
            hash.update(str(UTC()))
            self.nonce = hash.hexdigest()
        else:
            self.nonce = text

    def xml(self):
        root = Element('UsernameToken', ns=WSSENS)
        u = Element('Username', ns=WSSENS)
        u.setText(self.username)
        root.append(u)
        if self.password is not None:
            p = Element('Password', ns=WSSENS)
            p.setText(self.password)
            p.set('Type', PASSWORDTEXT_TYPE)
            root.append(p)
        if self.autosetnonce:
            self.setnonce()
        if self.nonce is not None:
            n = Element('Nonce', ns=WSSENS)
            n.setText(self.nonce)
            n.set('EncodingType', BASE64_ENC_TYPE)
            root.append(n)
        if self.autosetcreated:
            self.setcreated()
        if self.created:
            n = Element('Created', ns=WSUNS)
            n.setText(str(UTC(self.created)))
            root.append(n)
        return root


class _WsseKeywords(object):

    def apply_security_timestamp(self, duration='90 seconds'):
        """Applies a Timestamp element to future requests valid for the given `duration`.

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

    def apply_username_token(self, username, password=None, setcreated=False, setnonce=False):
        """Applies a UsernameToken element to future requests.

        The SOAP header will contain a UsernameToken element as specified in
        the WS-Security extension. The password type is PasswordText (plain
        text). The Created and Nonce values, if enabled, are generated
        automatically and updated every time a request is made."""
        setcreated = to_bool(setcreated)
        setnonce = to_bool(setnonce)
        token = AutoUsernameToken(username, password, setcreated, setnonce)
        wsse = self._get_wsse()
        wsse.tokens = [x for x in wsse.tokens if not isinstance(x, UsernameToken)]
        wsse.tokens.append(token)
        self._client().set_options(wsse=wsse)

    # private

    def _get_wsse(self, create=True):
        wsse = self._client().options.wsse
        if wsse is None and create:
            wsse = Security()
        return wsse
