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

import os
import urllib
import sys
from urlparse import urlparse
import xml.dom.minidom
from suds.client import Client
from suds import WebFault
from suds.sudsobject import Object as SudsObject
from suds.sax.document import Document
from suds.xsd.doctor import ImportDoctor, Import
from suds.xsd.sxbasic import Import as BasicImport
from suds.sax.enc import Encoder
from suds.sax.text import Raw
from suds.plugin import MessagePlugin
from suds.transport.http import HttpAuthenticated
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robot.utils import ConnectionCache


def to_bool(item):
    return BuiltIn().convert_to_boolean(item)


class _Options(object):

    def set_service(self, service):
        """Use the given `service` in future calls.
        
        `service` should be the name or the index of the service as it appears in the WSDL.
        """
        service = self._parse_index(service)
        self._client().set_options(service=service)

    def set_port(self, port):
        """Use the given `port` in future calls.
        
        `port` should be the name or the index of the port as it appears in the WSDL.
        """
        port = self._parse_index(port)
        self._client().set_options(port=port)

    def set_proxies(self, *protocol_url_pairs):
        """Controls http proxy settings.
        
        | Set Proxy | http | localhost:5000 | https | 10.0.4.23:80 |
        """
        if len(protocol_url_pairs) % 2 != 0:
            raise ValueError("There should be an even number of protocol-url pairs.")
        proxy = {}
        for i in range(0, len(protocol_url_pairs), 2):
            proxy[protocol_url_pairs[i]] = protocol_url_pairs[i+1]
        self._client().set_options(proxy=proxy)

    def set_headers(self, *dict_or_key_value_pairs):
        """Specify _extra_ http headers to send.
        
        Example:
        | Set Headers | X-Requested-With  | autogen          | # using key-value pairs |
        | ${headers}= | Create Dictionary | X-Requested-With | autogen                 |
        | Set Headers | ${headers}        |                  | # using a dictionary    |
        """
        length = len(dict_or_key_value_pairs)
        if length == 1:
            headers = dict_or_key_value_pairs[0]
        elif length % 2 == 0:
            headers = {}
            for i in range(0, len(dict_or_key_value_pairs), 2):
                headers[dict_or_key_value_pairs[i]] = dict_or_key_value_pairs[i+1]
        else:
            raise ValueError("There should be an even number of name-value pairs.")
        self._client().set_options(headers=headers)

    def set_soap_headers(self, *headers):
        """Specify SOAP headers.
        
        Example:
        | ${auth header}=           | Create Wsdl Object | AuthHeader           |          |          |       |
        | Set Wsdl Object Attribute | ${auth header}     | UserName             | gcarlson |          |       |
        | Set Wsdl Object Attribute | ${auth header}     | Password             | heyOh    |          |       |
        | Set Soap Headers          | ${auth header}     | # using WSDL object  |          |          |       |
        | ${auth dict}=             | Create Dictionary  | UserName             | sjenson  | Password | power |
        | Set Soap Headers          | ${auth dict}       | # using a dictionary |          |          |       |
        """
        self._client().set_options(soapheaders=headers)
    
    def set_return_xml(self, return_xml):
        """Set whether to return XML in future calls.
        
        The default value is _False_. If `return_xml` is True, then return the 
        SOAP envelope as a string in future calls. Otherwise, return a Python 
        object graph.
        
        See also `Call Soap Method`, `Call Soap Method Expecting Fault`, and `Specific Soap Call`.
        """
        self._set_boolean_option('retxml', return_xml)

    def set_xstq(self, xstq):
        """Set the XML schema type qualified flag.
        
        The XML schema type qualified flag indicates that _xsi:type_ attribute 
        *values* should be qualified by namespace.
        
        Default value is _True_.
        """
        self._set_boolean_option('xstq', xstq)

    def set_autoblend(self, autoblend):
        """Set the autoblend flag.
        
        The autoblend flag that ensures that the schema(s) defined within the 
        WSDL import each other.
        
        Default value is _False_.
        """
        self._set_boolean_option('autoblend', autoblend)

    def _set_boolean_option(self, name, value):
        value = to_bool(value)
        self._client().set_options(**{name: value})

    def _backup_options(self):
        options = self._client().options
        self._old_options = dict([[n, getattr(options, n)] for n in ('service', 'port')])

    def _restore_options(self):
        self._client().set_options(**self._old_options)


class SudsLibrary(_Options):
    """Library for functional testing of SOAP-based web services."""

    ROBOT_LIBRARY_SCOPE = "TEST"
    ROBOT_LIBRARY_DOC_FORMAT = "ROBOT"

    def __init__(self):
        self._url = None
        self._cache = ConnectionCache(no_current_msg='No current client')
        self._imports = []
        self._listener = _SudsListener()

    def create_client(self, url_or_path, alias=None):
        """Loads the WSDL from the given URL or path and creates a Suds client.
        
        Returns the index of this client instance which can be used later to
        switch back to it. See `Switch Client` for example.

        Optional alias is an alias for the client instance and it can be used
        for switching between clients (just as index can be used). See `Switch
        Client` for more details.
        
        | Create Client | http://localhost:8080/ws/Billing.asmx?WSDL |
        | Create Client | ${CURDIR}/../wsdls/tracking.wsdl |
        """
        self._url = self._get_url(url_or_path)
        kwargs = {'plugins': (self._listener,)}
        imports = self._imports
        if imports:
            self._log_imports()
            kwargs['doctor'] = ImportDoctor(*imports)
        #if 'credentials' in options:
        #    kwargs['transport'] = HttpAuthenticated(username=options['credentials']['username'], password=options['credentials']['password'])
        client = Client(self._url, **kwargs)
        client.set_options(faults=True)
        logger.info('Using WSDL at %s%s' % (self._url, client))
        self._imports = []
        return self._cache.register(client, alias)

    def switch_client(self, index_or_alias):
        """Switches between clients using index or alias.

        Index is returned from `Create Client` and alias can be given to it.

        Example:
        | Create Client  | http://localhost:8080/Billing?wsdl   | Billing   |
        | Create Client  | http://localhost:8080/Marketing?wsdl | Marketing |
        | Call           | sendSpam                             |           |
        | Switch Client  | Billing                              | # alias   |
        | Call           | sendInvoices                         |           |
        | Switch Client  | 2                                    | # index   |

        Above example expects that there was no other clients created when
        creating the first one because it used index '1' when switching to it
        later. If you aren't sure about that you can store the index into
        a variable as below.

        | ${id} =            | Create Client  | ... |
        | # Do something ... |                |     |
        | Switch Client      | ${id}          |     |
        """
        self._cache.switch(index_or_alias)
    
    def set_wsdl_object_attribute(self, object, name, value):
        """Sets the attribute of a WSDL object ."""
        self._assert_is_suds_object(object)
        assert hasattr(object, name), "object has no attribute '%s'" % name
        setattr(object, name, value)

    def get_wsdl_object_attribute(self, object, name):
        """Gets the attribute of a WSDL object.
        
        Extendend variable syntax may be used to access attributes; however, 
        some WSDL objects may have attribute names that are illegal in Python, 
        necessitating this keyword.
        """
        self._assert_is_suds_object(object)
        return getattr(object, name)

    def create_wsdl_object(self, type, *key_value_pairs):
        """Creates a WSDL object of the specified `type`.
        
        Requested `type` must be defined in the WSDL or in an import specified 
        by the WSDL or with `Add Doctor Import`.
        
        Example:
        | ${contact}=               | Create Wsdl Object | Contact |              |              |
        | Set Wsdl Object Attribute | ${contact}         | Name    | Kelly Newman |              |
        | ${contact}=               | Create Wsdl Object | Contact | Name         | Kelly Newman |
        """
        if len(key_value_pairs) % 2 != 0:
            raise ValueError("Creating a WSDL object failed. There should be "
                             "an even number of name-value pairs.")
        obj = self._client().factory.create(type)
        for i in range(0, len(key_value_pairs), 2):
            self.set_attribute(obj, key_value_pairs[i], key_value_pairs[i+1])
        return obj

    def call_soap_method(self, name, *args):
        """Call the SOAP method with the given `name` and `args`.
        
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
        """Call the SOAP method expecting the server to raise a fault.
        
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

    def set_location(self, url, service_index=-1, *names):
        """Set location to use in future calls.
        
        This is for when the location(s) specified in the WSDL are not correct. 
        `service` is the index of the service to alter locations for and not 
        used if there is only one service defined. If `service` is less than 0, 
        then set the location on all services. If no methods names are given, 
        then sets the location for all methods.
        """
        wsdl = self._client().wsdl
        service_count = len(wsdl.services)
        service_index = 0 if (service_count==1) else int(service_index)
        names = names if names else None
        if service_index < 0:
            for svc in wsdl.services:
                svc.setlocation(url, names)
        else:
            wsdl.services[service_index].setlocation(url, names)

    def add_doctor_import(self, import_namespace, location=None, *filters):
        """Add an import be used in the next client.
        
        Doctor imports are applied to the _next_ client created with 
        `Create Client`. Doctor imports are necessary when the references are 
        made in one schema to named objects defined in another schema without 
        importing it. Use location ${None} if you do not want to specify the 
        location but want to specify filters. The following example would 
        import the SOAP encoding schema into only the namespace 
        http://some/namespace/A:
        | Add Doctor Import | http://schemas.xmlsoap.org/soap/encoding/ | ${None} | http://some/namespace/A |
        """
        location = location if location else None
        imp = Import(import_namespace, location)
        for filter in filters:
            imp.filter.add(filter)
        self._imports.append(imp)

    def bind_schema_to_location(self, namespace, location):
        """Sets the `location` for the given `namespace` of a schema.
        
        This is for when an import statement specifies a schema but not its 
        location. If the schemaLocation is present and incorrect, this will 
        not override that. Bound schemas are shared amongst all instances of 
        SudsLibrary. Schemas should be bound if necessary before `Add Doctor 
        Import` or `Create Client` where appropriate.
        """
        BasicImport.bind(namespace, location)

    # private
   
    def _client(self):
        if not self._cache.current:
            raise RuntimeError('No client was created')
        return self._cache.current

    def _log_imports(self):
        if self._imports:
            msg = "Using Imports for ImportDoctor:"
            for imp in self._imports:
                msg += "\n   Namespace: '%s' Location: '%s'" % (imp.ns, imp.location)
                for ns in imp.filter.tns:
                    msg += "\n      Filtering for namespace '%s'" % ns
            logger.info(msg)

    def _call(self, service, port, expect_fault, name, *args):
        client = self._client()
        self._backup_options()
        if service:
            client.set_options(service=self._parse_index(service))
        if port:
            client.set_options(port=self._parse_index(port))
        method = getattr(client.service, name)
        self._listener.location = method.method.location
        retxml = client.options.retxml
        args = [self._encode_if_necessary(arg) for arg in args]
        received =  None
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

    def _encode_if_necessary(self, arg):
        if Encoder().needsEncoding(arg):
            arg = Raw(arg)
        return arg

    def _get_url(self, url_or_path):
        if not len(urlparse(url_or_path).scheme) > 1:
            if not os.path.isfile(url_or_path):
                raise IOError("File '%s' not found." % url_or_path)
            url_or_path = 'file:' + urllib.pathname2url(url_or_path)
        return url_or_path

    def _parse_index(self, s):
        try:
            return int(s)
        except (ValueError, TypeError):
            return s

    def _assert_is_suds_object(self, object):
        assert isinstance(object, SudsObject), "object must be a WSDL object(suds.sudsobject.Object)"
    

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


py_version = sys.version_info[0] + sys.version_info[1] * 0.1
if py_version < 3.3:
    class _ElementMonkeyPathes(object):
        # from http://ronrothman.com/public/leftbraned/xml-dom-minidom-toprettyxml-and-silly-whitespace/

        def fixed_writexml(self, writer, indent="", addindent="", newl=""):
            writer.write(indent+"<" + self.tagName)
            attrs = self._get_attributes()
            a_names = attrs.keys()
            a_names.sort()
            for a_name in a_names:
                writer.write(" %s=\"" % a_name)
                xml.dom.minidom._write_data(writer, attrs[a_name].value)
                writer.write("\"")
            if self.childNodes:
                if len(self.childNodes) == 1 \
                  and self.childNodes[0].nodeType == xml.dom.minidom.Node.TEXT_NODE:
                    writer.write(">")
                    self.childNodes[0].writexml(writer, "", "", "")
                    writer.write("</%s>%s" % (self.tagName, newl))
                    return
                writer.write(">%s"%(newl))
                for node in self.childNodes:
                    node.writexml(writer,indent+addindent,addindent,newl)
                writer.write("%s</%s>%s" % (indent,self.tagName,newl))
            else:
                writer.write("/>%s"%(newl))

        xml.dom.minidom.Element.writexml = fixed_writexml


class _DocumentMonkeyPatches(object):
    # fixes AttributeError in debug log event that fails the keyword

    def str(self):
        s = []
        s.append(self.DECL)
        s.append('\n')
        s.append(self.root().str() if self.root() is not None else '<empty>')
        return ''.join(s)

    Document.str = str
