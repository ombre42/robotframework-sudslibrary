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
from .soaplogging import _SoapLoggingKeywords
from suds import null
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

THIS_DIR = dirname(abspath(__file__))
execfile(join(THIS_DIR, 'version.py'))

__version__ = VERSION


class SudsLibrary(_ClientManagementKeywords, _FactoryKeywords,
                  _OptionsKeywords, _ProxyKeywords, _SoapLoggingKeywords):
    """SudsLibrary is a library for functional testing of SOAP-based web
    services.

    == Creating and Configuring a Client ==
    If necessary, use keywords `Bind Schema To Location` or `Add Doctor
    Import`. These are rarely needed. Next, `Create Client` to create a Suds
    client. The output from this keyword contains useful information including
    available types and methods. Next, the Set * keywords may then be used to
    configure the client if necessary. `Set Location` is the most commonly
    needed setting keyword.

    == Working With WSDL Objects ==
    When Suds digests a WSDL, it creates dynamic types to represent the
    complex types defined by the WSDL or its imports. These types may be used
    for method arguments, return values or both. `Create Wsdl Object` is used
    to create instances of WSDL objects to be used as arguments. A WSDL object
    returned by one method may also be used as an argument to another.
    `Set Wsdl Object Attribute` sets a WSDL object's attributes. Retrieving a
    WSDL object's attribute values may be done with either `Get Wsdl Object
    Attribute` or using extended variable syntax like ${object.attribute}. The
    keywords in the _BuiltIn_ and _Collections_ libraries may be used to
    verify attribute values.

    == Example Test ==
    You can run this test because it uses a public web service.

    | Create Client              | http://www.webservicex.net/Statistics.asmx?WSDL |               |              |
    | ${dbl array}=              | Create Wsdl Object                              | ArrayOfDouble |              |
    | Append To List             | ${dbl array.double}                             | 2.0           |              |
    | Append To List             | ${dbl array.double}                             | 3.0           |              |
    | ${result}=                 | Call Soap Method                                | GetStatistics | ${dbl array} |
    | Should Be Equal As Numbers | ${result.Average}                               | 2.5           |              |

    The definition of type ArrayOfDouble:
    | <s:complexType name="ArrayOfDouble">
    |   <s:sequence>
    |     <s:element minOccurs="0" maxOccurs="unbounded" name="double" type="s:double"/>
    |   </s:sequence>
    | </s:complexType>
    Note that the attribute name on the ArrayOfDouble-type that is the list of
    numbers is the singular "double". Outside of the WSDL, the structure can
    also be seen in the output of Create Wsdl Object:
    | ${dbl array} = (ArrayOfDouble){
    |   double[] = <empty>
    | }

    The relevant part of the WSDL defining the parameters to the method:
    | <s:element name="GetStatistics">
    |   <s:complexType>
    |     <s:sequence>
    |       <s:element minOccurs="0" maxOccurs="1" name="X" type="tns:ArrayOfDouble"/>
    |     </s:sequence>
    |   </s:complexType>
    | </s:element>
    The definition of this method appears in the output of Create Client as:
    | GetStatistics(ArrayOfDouble X, )

    === Passing Explicit NULL Values ===
    If you have a service that takes NULL values for required parameters or
    you want to pass NULL for optional object attributes, you simply need to
    set the value to ${SUDS_NULL}. You need to use ${SUDS_NULL} instead of
    ${None} because None is interpreted by the marshaller as not having a
    value. The soap message will contain an empty (and xsi:nil="true" if node
    defined as nillable). ${SUDS_NULL} is defined during library
    initialization, so editors like RIDE will not show it as defined.

    == Extending SudsLibrary ==
    There may be times where Suds/SudsLibrary does not work using the library
    keywords alone. Extending the library instead of writing a custom one will
    allow you to use the existing keywords in SudsLibrary.

    There are two methods useful for extending SudsLibrary:
    | _client()
    | _add_client(client, alias=None)
    The first can be used to access the current instance of
    suds.client.Client. The second can be used to put a client into the client
    cache that you have instantiated.

    Here is an example demonstrating how to implement a keyword that adds a
    MessagePlugin to the current Suds client (based on the [https://fedorahosted.org/suds/wiki/Documentation#MessagePlugin|Suds documentation]):
    | from robot.libraries.BuiltIn import BuiltIn
    | from suds.plugin import MessagePlugin
    |
    | class _MyPlugin(MessagePlugin):
    |     def marshalled(self, context):
    |         body = context.envelope.getChild('Body')
    |         foo = body[0]
    |         foo.set('id', '12345')
    |         foo.set('version', '2.0')
    |
    | class SudsLibraryExtensions(object):
    |     def attach_my_plugin(self):
    |         client = BuiltIn().get_library_instance("SudsLibrary")._client()
    |         # append so SudsLibrary's plugin is left in place
    |         plugins = client.options.plugins
    |         if any(isinstance(x, _MyPlugin) for x in plugins):
    |             return
    |         plugins.append(_MyPlugin())
    |         client.set_options(plugins=plugins)
    """

    ROBOT_LIBRARY_VERSION = VERSION
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_DOC_FORMAT = "ROBOT"

    def __init__(self):
        self._cache = ConnectionCache(no_current_msg='No current client')
        self._imports = []
        self._logger = logger
        try:  # exception if Robot is not running
            BuiltIn().set_global_variable("${SUDS_NULL}", null())
        except:
            pass
