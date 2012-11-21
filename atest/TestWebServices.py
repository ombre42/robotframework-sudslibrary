# -*- coding: utf-8 -*-
from ladon.server.wsgi import LadonWSGIApplication
import wsgiref.simple_server
from os.path import abspath,dirname,join
import subprocess

scriptdir = dirname(abspath(__file__))
service_modules = ['calculator','testservice']
port = 8080

class LadonServer():

    def start(self):
        application = self._create_application()
        self.server = wsgiref.simple_server.make_server('', port, application)
        self.server.serve_forever()
        
    def _create_application(self):
        return LadonWSGIApplication(
            service_modules,
            [join(scriptdir,'services')],
            catalog_name = 'Services for testing SudsLibrary',
            catalog_desc = 'Ladon cannot cover many use cases for Suds, but it is easy to set up and generates WSDLs.')

class TestWebServices(object):

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def start_services(self):
        self.server = subprocess.Popen(['python', abspath(__file__)])

    def stop_services(self):
        self.server.kill()
    
if __name__=='__main__':
    print("\nExample services are running on port %(port)s.\nView browsable API at http://localhost:%(port)s\n" % {'port':port})
    LadonServer().start()
