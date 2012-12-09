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

from os.path import abspath, dirname, join
from robot.utils import ConnectionCache
from .monkeypatches import *
from .plugins import _SudsListener
from .factory import _FactoryKeywords
from .clientmanagement import _ClientManagementKeywords
from .options import _OptionsKeywords
from .proxy import _ProxyKeywords
from robot.api import logger

THIS_DIR = dirname(abspath(__file__))
execfile(join(THIS_DIR, 'version.py'))

__version__ = VERSION

class SudsLibrary(_ClientManagementKeywords, _FactoryKeywords, 
                  _OptionsKeywords, _ProxyKeywords):
    """Library for functional testing of SOAP-based web services."""

    ROBOT_LIBRARY_VERSION = VERSION
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_DOC_FORMAT = "ROBOT"

    def __init__(self):
        self._cache = ConnectionCache(no_current_msg='No current client')
        self._imports = []
        self._listener = _SudsListener()
        self._logger = logger
