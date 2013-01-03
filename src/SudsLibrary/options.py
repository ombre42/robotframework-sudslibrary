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

from suds.xsd.doctor import Import
from suds.xsd.sxbasic import Import as BasicImport
from suds import ServiceNotFound
from suds.transport.https import HttpAuthenticated
from suds.transport.https import WindowsHttpAuthenticated
from suds.transport.http import HttpAuthenticated as AlwaysSendTransport
from .utils import *


class _OptionsKeywords(object):

    def set_service(self, service):
        """Sets the `service` to use in future requests.

        `service` should be the name or the index of the service as it appears in the WSDL.
        """
        service = parse_index(service)
        self._client().set_options(service=service)

    def set_port(self, port):
        """Sets the `port` to use in future requests.

        `port` should be the name or the index of the port as it appears in the WSDL.
        """
        port = parse_index(port)
        self._client().set_options(port=port)

    def set_proxies(self, *protocol_url_pairs):
        """Sets the http proxy settings.

        | Set Proxy | http | localhost:5000 | https | 10.0.4.23:80 |
        """
        if len(protocol_url_pairs) % 2 != 0:
            raise ValueError("There should be an even number of protocol-url pairs.")
        proxy = {}
        for i in range(0, len(protocol_url_pairs), 2):
            proxy[protocol_url_pairs[i]] = protocol_url_pairs[i+1]
        self._client().set_options(proxy=proxy)

    def set_headers(self, *dict_or_key_value_pairs):
        """Sets _extra_ http headers to send in future requests.

        Example:
        | Set Headers | X-Requested-With  | autogen          | # using key-value pairs |
        or using a dictionary:
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
        """Sets SOAP headers to send in future requests.

        Example:
        | ${auth header}=           | Create Wsdl Object | AuthHeader           |          |
        | Set Wsdl Object Attribute | ${auth header}     | UserName             | gcarlson |
        | Set Wsdl Object Attribute | ${auth header}     | Password             | heyOh    |
        | Set Soap Headers          | ${auth header}     | # using WSDL object  |          |
        or using a dictionary:
        | ${auth dict}=             | Create Dictionary  | UserName             | gcarlson  | Password | heyOh |
        | Set Soap Headers          | ${auth dict}       | # using a dictionary |           |          |       |
        """
        self._client().set_options(soapheaders=headers)
    
    def set_return_xml(self, return_xml):
        """Sets whether to return XML in future requests.

        The default value is _False_. If `return_xml` is True, then return the 
        SOAP envelope as a string in future requests. Otherwise, return a 
        Python object graph.

        See also `Call Soap Method`, `Call Soap Method Expecting Fault`, and `Specific Soap Call`.
        
        Example:
        | ${old value}= | Set Return Xml | True |
        """
        old_value = self._client().options.retxml
        self._set_boolean_option('retxml', return_xml)
        return old_value

    def set_http_authentication(self, username, password, type='STANDARD'):
        """Sets http authentication type and credentials.
        
        Available types are STANDARD, ALWAYS_SEND, and NTLM. Type STANDARD 
        will only send credentials to the server upon request (HTTP/1.0 401 
        Authorization Required) by the server only. Type ALWAYS_SEND will 
        cause an Authorization header to be sent in every request. Type NTLM 
        requires the python-ntlm package to be installed, which is not 
        packaged with Suds or SudsLibrary.
        """
        classes = {
            'STANDARD': HttpAuthenticated,
            'ALWAYS_SEND': AlwaysSendTransport,
            'NTLM': WindowsHttpAuthenticated
        }
        try:
            _class = classes[type.upper()]
        except KeyError:
            raise ValueError("'%s' is not a supported type." % type)
        transport = _class(username=username, password=password)
        self._client().set_options(transport=transport)

    def set_location(self, url, service='ALL_SERVICES', *names):
        """Sets location to use in future requests.

        This is for when the location(s) specified in the WSDL are not correct. 
        `service` is the name or index of the service to change and ignored 
        unless there is more than one service. If `service` is ALL_SERVICES, 
        then set the location on all services. If no methods names are given, 
        then sets the location for all methods.
        """
        wsdl = self._client().wsdl
        service_count = len(wsdl.services)
        service = 0 if (service_count==1) else parse_index(service)
        names = names if names else None
        if service == 'ALL_SERVICES':
            for svc in wsdl.services:
                svc.setlocation(url, names)
        elif isinstance(service, int):
            wsdl.services[service].setlocation(url, names)
        else:
            found = False
            for svc in  wsdl.services:
                if svc.name == service:
                    svc.setlocation(url, names)
                    return
            raise ServiceNotFound, service

    def add_doctor_import(self, import_namespace, location=None, *filters):
        """Adds an import be used in the next client.

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

    def set_soap_logging(self, log):
        """Sets whether to log the request and response for the current client.
        
        Logging is enabled by default. Disabling logging will reduce the size 
        of the log. Returns the current value.
        
        Example:
        | ${old log setting} | Set Soap Logging | True |
        """
        client = self._client()
        old_value = self._logging_option[client]
        new_value = to_bool(log)
        self._logging_option[client] = new_value
        self._listener.log = new_value
        return old_value

    # private

    def _set_boolean_option(self, name, value):
        value = to_bool(value)
        self._client().set_options(**{name: value})

    def _backup_options(self):
        options = self._client().options
        self._old_options = dict([[n, getattr(options, n)] for n in ('service', 'port')])

    def _restore_options(self):
        self._client().set_options(**self._old_options)