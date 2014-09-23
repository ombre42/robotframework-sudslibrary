# -*- coding: utf-8 -*-
from ladon.ladonizer import ladonize
from ladon.types.ladontype import LadonType
from ladon.compat import PORTABLE_STRING

class Person(LadonType):

    first_name = PORTABLE_STRING
    last_name = PORTABLE_STRING


class TestService(object):
    
    @ladonize(PORTABLE_STRING, PORTABLE_STRING, rtype=Person)
    def returnComplexType(self, first_name, last_name):
        person = Person()
        person.first_name = first_name
        person.last_name = last_name
        return person

    @ladonize(Person, rtype=PORTABLE_STRING)
    def complexTypeArgument(self, person):
        return ' '.join((person.first_name, person.last_name))

    @ladonize(rtype=int)
    def theAnswer(self):
        return 42

    @ladonize(PORTABLE_STRING, rtype=PORTABLE_STRING)
    def fault(self, fault_string):
        raise RuntimeError(fault_string)
