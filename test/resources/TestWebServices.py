import subprocess
from os.path import abspath, dirname, join
from tempfile import TemporaryFile
import time
import urllib


class TestWebServices(object):

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def start_services(self, server_type):
        server_type = server_type.upper().replace(' ', '')
        if server_type not in ['CHERRYPY', 'WSGIREF']:
            raise ValueError("server_type must be CHERRYPY or WSGIREF. "
                             "got %s" % server_type)
        # launch with python because ladon does not work under Jython 2.5
        script = join(dirname(abspath(__file__)), 'TestServer.py')
        self.server = subprocess.Popen(['python', script, server_type],
                                       stdout=TemporaryFile(),
                                       stderr=subprocess.STDOUT)
        for i in range(10):
            try:
                f = urllib.urlopen('http://localhost:8080/')
                resp = f.read()
                if "Ladon" in resp:  # getcode() not avail on 2.5
                    return
            except IOError, err:
                print err.message
            time.sleep(1)
        raise RuntimeError('Server did not respond in the allotted time')

    def stop_services(self):
        # exit via special URL because Jython 2.5 lacks good subprocess features
        urllib.urlopen('http://localhost:8080/exit')
        time.sleep(2)
        if self.server.poll() is None:
            raise RuntimeError("Server failed to shutdown!")
