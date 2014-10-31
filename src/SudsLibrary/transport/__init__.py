"""Contains the transport classes from suds-jurko, modified to close connections.

See http://bugs.jython.org/issue2170
Jython 2.5 does not close connections properly when they get garbage collected.
This can cause the client or the server to run out of sockets.
HttpTransport.open has been altered to explicitly close the connection to avoid
this.

Minor adjustments to the imports were made. A string type assertion was removed.
"""

from http import HttpTransport
from http import HttpAuthenticated as AlwaysSendTransport
from https import HttpAuthenticated
from https import WindowsHttpAuthenticated
