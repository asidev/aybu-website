#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010 Asidev s.r.l.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
from setuptools import setup, find_packages

name = 'aybu-website'
version = ":versiontools:aybu.website:"
description = 'aybu-website'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
long_description = README + '\n\n' + CHANGES

classifiers = ("Programming Language :: Python",
               "Framework :: Pyramid", "Topic :: Internet :: WWW/HTTP",
               "Topic :: Internet :: WWW/HTTP :: WSGI :: Application")

author = 'Asidev s.r.l.'
author_email = 'info@asidev.com'
url = 'https://bitbucket.org/asidev/aybu-website'
keywords = ''

include_package_data = True
zip_safe = False

requires = ('pyramid<1.3a', 'WebError', 'SQLAlchemy<0.8a', 'Pillow',
            'Babel', 'recaptcha-client', 'WebHelpers', 'Mako',
            'aybu-core', 'aybu-themes',  'pyramid_mailer',
            'pyramid_debugtoolbar', 'pyramid_exclog')

tests_require = ('nose', 'coverage', 'webtest', 'aybu-instances-website-tests')
setup_requires = ('versiontools >= 1.8',)

test_suite = 'tests'

entry_points = """\
[paste.app_factory]
    main = aybu.website:main
[paste.paster_command]
    aybu-setup = aybu.core.utils.command:SetupApp
    uwsgi = pasteuwsgi.serve:ServeCommand
"""

paster_plugins = ['pyramid']
namespace_packages = ['aybu']
message_extractors = {
    'aybu.website': [
        ('**.py', 'python', None),
        ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
        ('static/**', 'ignore', None)
    ],
    'aybu.themes': [
        ('*/templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
        ('*/static/**', 'ignore', None)

    ]
}

"""
Messages have to extracted also from
- aybu.themes
- instance
"""

setup(name=name, version=version, description=description,
      long_description=long_description, classifiers=classifiers,
      author=author, author_email=author_email, url=url, keywords=keywords,
      packages=find_packages(), include_package_data=include_package_data,
      zip_safe=zip_safe, install_requires=requires, tests_require=tests_require,
      test_suite=test_suite, entry_points=entry_points,
      message_extractors=message_extractors,
      paster_plugins=paster_plugins, namespace_packages=namespace_packages,
      setup_requires=setup_requires)
