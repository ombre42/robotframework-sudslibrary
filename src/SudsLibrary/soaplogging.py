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

import xml.dom.minidom
from xml.parsers.expat import ExpatError
from suds.plugin import MessagePlugin
from robot.api import logger
from .utils import *


class _SoapLogger(MessagePlugin):

    def __init__(self):
        self._sent = None
        self._received = None
        self.log = True

    def sending(self, context):
        self._sent = context.envelope
        self._received = None
        if self.log:
            logger.info('Sending:\n%s' % self.last_sent(True))

    def last_sent(self, pretty=False):
        # possible that text inserted into the post body, making it invalid XML
        try:
            return self._prettyxml(self._sent) if pretty else self._sent
        except ExpatError:
            return self._sent

    def received(self, context):
        self._received = context.reply
        if self.log:
            logger.info('Received:\n%s' % self.last_received(True))

    def last_received(self, pretty=False):
        return self._prettyxml(self._received) if pretty else self._received

    def _prettyxml(self, xml_string):
        dom = xml.dom.minidom.parseString(xml_string)
        return dom.toprettyxml(indent="  ")


class _SoapLoggingKeywords(object):

    def set_soap_logging(self, log):
        """Sets whether to log the request and response for the current client.

        Logging is enabled by default. The message sent and received is logged
        at level INFO. The XML is formatted for readability. Disabling logging
        will reduce the size of the log. Returns the current value.

        Example:
        | ${old log setting} | Set Soap Logging | False |
        """
        new_value = to_bool(log)
        soap_logger = self._get_soap_logger()
        if soap_logger:
            old_value = soap_logger.log
        else:
            soap_logger = self._add_soap_logger()
            old_value = False
        soap_logger.log = new_value
        return old_value

    def get_last_sent(self):
        """Gets the message text last sent.

        Unless a plugin is used to modify the message, it will always be a XML
        document."""
        soap_logger = self._get_soap_logger(True)
        return soap_logger.last_sent(False)

    def get_last_received(self):
        """Gets the XML last received."""
        soap_logger = self._get_soap_logger(True)
        return soap_logger.last_received(False)

    # private

    def _get_soap_logger(self, required=False):
        plugins = self._client().options.plugins
        matches = filter(lambda x: isinstance(x, _SoapLogger), plugins)
        if matches:
            return matches[0]
        else:
            if required:
                raise RuntimeError("The SudsLibrary SOAP logging message plugin has been removed.")
            return None

    def _add_soap_logger(self):
        client = self._client()
        plugins = client.options.plugins
        soap_logger = _SoapLogger()
        plugins.append(soap_logger)
        client.set_options(plugins=plugins)
        return soap_logger
