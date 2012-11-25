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

from suds.plugin import MessagePlugin
from robot.api import logger
from .monkeypatches import *


class _SudsListener(MessagePlugin):

    def __init__(self):
        self._sent = None
        self._received = None
        self.location = 'UNKOWN'

    def sending(self, context):
        self._sent = context.envelope
        self._received = None
        logger.info('Sending to %s:\n%s' % (self.location, self.last_sent(True)))

    def last_sent(self, pretty=False):
        return self._prettyxml(self._sent) if pretty else self._sent

    def received(self, context):
        self._received = context.reply
        logger.info('Received:\n%s' % self.last_received(True))

    def last_received(self, pretty=False):
        return self._prettyxml(self._received) if pretty else self._received

    def _prettyxml(self, xml_string):
        dom = xml.dom.minidom.parseString(xml_string)
        return dom.toprettyxml(indent="  ")