# Copyright 2012 Kevin Ormbrek
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

from suds import WebFault
from .utils import *


class _ProxyKeywords(object):

    def call_soap_method(self, name, *args):
        """Calls the SOAP method with the given `name` and `args`.

        Returns a Python object graph or SOAP envelope as a XML string
        depending on the client options.
        """

        return self._call(None, None, False, name, *args)

    def specific_soap_call(self, service, port, name, *args):
        """Calls the SOAP method overriding client settings.

        If there is only one service specified then `service` is ignored.
        `service` and `port` can be either by name or index. If only `port` or
        `service` need to be specified, leave the other one blank. The index
        is the order of appearence in the WSDL starting with 0.

        Returns a Python object graph or SOAP envelope as a XML string
        depending on the client options.
        """

        return self._call(service, port, False, name, *args)

    def call_soap_method_expecting_fault(self, name, *args):
        """Calls the SOAP method expecting the server to raise a fault.

        Fails if the server does not raise a fault.  Returns a Python object
        graph or SOAP envelope as a XML string depending on the client
        options.

        A fault has the following attributes:\n
        | faultcode   | required |
        | faultstring | required |
        | faultactor  | optional |
        | detail      | optional |
        """
        return self._call(None, None, True, name, *args)

    # private

    def _call(self, service, port, expect_fault, name, *args):
        client = self._client()
        self._backup_options()
        if service:
            client.set_options(service=parse_index(service))
        if port:
            client.set_options(port=parse_index(port))
        method = getattr(client.service, name)
        retxml = client.options.retxml
        received = None
        try:
            received = method(*args)
            # client does not raise fault when retxml=True, this will cause it to be raised
            if retxml:
                binding = method.method.binding.input
                binding.get_reply(method.method, received)
            if expect_fault:
                raise AssertionError('The server did not raise a fault.')
        except WebFault, e:
            if not expect_fault:
                raise e
            if not retxml:
                received = e.fault
        finally:
            self._restore_options()
        return received

    # private

    def _backup_options(self):
        options = self._client().options
        self._old_options = dict([[n, getattr(options, n)] for n in ('service', 'port')])

    def _restore_options(self):
        self._client().set_options(**self._old_options)
