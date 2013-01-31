#!/usr/bin/env python

import os
import sys
from os.path import join, dirname

sys.path.append(join(dirname(__file__), 'src'))
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

execfile(join(dirname(__file__), 'src', 'SudsLibrary', 'version.py'))

DESCRIPTION = """
SudsLibrary is a web service testing library for Robot Framework
that leverages Suds to test SOAP-based services.
""".strip()

CLASSIFIERS  = """
Development Status :: 4 - Beta
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Testing
""".strip().splitlines()

# determine whether to use Jurko's fork of Suds. This will only work for source
# distributions.
jurko = False
try:
    import suds
    jurko = 'jurko' in suds.__version__
except:
    pass
suds_rqmnt = 'suds >= 0.4' if not jurko else 'suds-jurko'
suds_rqmnt = os.environ.get('SUDS_LIBRARY_SUDS_REQUIREMENT', suds_rqmnt)


setup(name         = 'robotframework-sudslibrary',
      version      = VERSION,
      description  = 'Robot Framework test library for SOAP-based services.',
      long_description = DESCRIPTION,
      author       = 'Kevin Ormbrek',
      author_email = '<kormbrek@gmail.com>',
      url          = 'https://github.com/ombre42/robotframework-sudslibrary',
      license      = 'Apache License 2.0',
      keywords     = 'robotframework testing testautomation soap suds web service',
      platforms    = 'any',
      classifiers  = CLASSIFIERS,
      zip_safe     = True,
      install_requires = [
                            suds_rqmnt,
                            'robotframework >= 2.6.0',
                         ],
      package_dir  = {'' : 'src'},
      packages     = ['SudsLibrary'],
      download_url = "https://github.com/ombre42/robotframework-sudslibrary/downloads"
      )