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
from suds import null
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

THIS_DIR = dirname(abspath(__file__))
execfile(join(THIS_DIR, 'version.py'))

__version__ = VERSION

class SudsLibrary(_ClientManagementKeywords, _FactoryKeywords, 
                  _OptionsKeywords, _ProxyKeywords):
    """Library for functional testing of SOAP-based web services.

    === Passing Explicit NULL Values ===
    If you have a service that takes NULL values for required parameters or 
    you want to pass NULL for optional object attributes, you simply need to 
    set the value to ${SUDS_NULL}. You need to use ${SUDS_NULL} instead of 
    ${None} because None is interpreted by the marshaller as not having a 
    value. The soap message will contain an empty (and xsi:nil="true" if node 
    defined as nillable). ${SUDS_NULL} is defined during library 
    initialization, so editors like RIDE will not show it as defined.
    """

    ROBOT_LIBRARY_VERSION = VERSION
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_DOC_FORMAT = "ROBOT"

    def __init__(self):
        self._cache = ConnectionCache(no_current_msg='No current client')
        self._imports = []
        self._listener = _SudsListener()
        self._logger = logger
        self._logging_option = {}
        try: # exception if Robot is not running
            BuiltIn().set_global_variable("${SUDS_NULL}", null()) 
        except:
            pass
