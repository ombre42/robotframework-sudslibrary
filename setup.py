#!/usr/bin/env python

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
"""[1:-1]

setup(name         = 'robotframework-sudslibrary',
      version      = VERSION,
      description  = 'Web service testing library for Robot Framework',
      long_description = DESCRIPTION,
      author       = 'Kevin Ormbrek',
      author_email = '<kormbrek@gmail.com>',
      url          = 'https://github.com/ombre42/robotframework-sudslibrary',
      license      = 'Apache License 2.0',
      keywords     = 'robotframework testing testautomation soap suds web service',
      platforms    = 'any',
      classifiers  = [
                        "Development Status :: 2 - Pre-Alpha",
                        "License :: OSI Approved :: Apache Software License",
                        "Operating System :: OS Independent",
                        "Programming Language :: Python",
                        "Topic :: Software Development :: Testing"
                     ],
      zip_safe     = True,
      install_requires = [
                            'suds >= 0.4',
                            'robotframework >= 2.6.0',
                         ],
      package_dir  = {'' : 'src'},
      packages     = ['SudsLibrary'],
      download_url = "https://github.com/ombre42/robotframework-sudslibrary/downloads"
      )