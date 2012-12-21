import logging


# because there is no RequestPlugin type in Suds, capture the request through a logging handler
class HttpHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)
        for module in ["suds.transport.http", "suds.transport.https"]:
            logger = logging.getLogger(module)
            logger.setLevel(logging.DEBUG)
            logger.addHandler(self)

    def emit(self, record):
        try:
            if record.msg=="sending:\n%s":
                self.request = record.args[0]
        except:
            return


class Loggers(object):

    handler = HttpHandler()
    
    def get_sent_request(self):
        """Returns last _suds.transport.Request_ sent"""
        return self.handler.request
