Suds library for Robot Framework
================================

Introduction
------------

This library is in a beta development stage.

See the working `Keyword Documentation`_ for more information about using the library.

Installation
------------

You can install SudsLibrary using pip, with the following command

  ``pip install robotframework-sudslibrary``

Installation Using a Fork of Suds
---------------------------------

Development on the Suds project has appeared to cease. There are more than one forks of Suds that you may want to use. SudsLibrary was only tested with suds-jurko and the official suds package.
Here are three ways to setup for using a fork:

1. If the fork is in PyPI:
Set the environmental variable SUDS_LIBRARY_SUDS_REQUIREMENT to a valid requirement string, such as "suds-somefork > 0.5". When SudsLibrary is installed, the fork will be installed from PyPi to satisfy the requirement.

2. If the fork is not in PyPI or you have already installed it:
Install the fork prior to SudsLibrary. Then set the environmental variable SUDS_LIBRARY_SUDS_REQUIREMENT to a space and install SudsLibrary. This essentially removes the installation dependency on Suds.

3. Uninstall suds after installing SudsLibrary. Then install a fork.

Jython Support
--------------

Suds and SudsLibrary do work under Jython. Suds will not install under Jython, however.
You can extract the contents of the source tarball and put that folder in JYTHONPATH (suds-0.4) or you can use the installation of Suds performed by CPython.
SudsLibrary will install under Jython only if you bypass the requirement on Suds as mentioned in the `Installation Using a Fork of Suds`_.
If you need to test services served over HTTPS in Jython and the certificates are not valid, you will have some extra work to do since Java always validates certificates.
See these posts on getting Java to trust all certificates:

1. http://tech.pedersen-live.com/2010/10/trusting-all-certificates-in-jython/
2. http://jython.xhaus.com/installing-an-all-trusting-security-provider-on-java-and-jython/

IronPython Support
------------------
Support under IronPython is unkown -- it has not been tested.

.. _Keyword Documentation: http://ombre42.github.com/robotframework-sudslibrary/doc/SudsLibrary.html