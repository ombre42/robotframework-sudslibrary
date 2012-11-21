# -*- coding: utf-8 -*-
from ladon.ladonizer import ladonize

class Calculator(object):

    """Exists so that there are two services to choose from."""

    @ladonize(int,int,rtype=int)
    def add(self,a,b):
        return a+b

