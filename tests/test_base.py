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

import json
import unittest
import ConfigParser
import os

from pyramid import testing

from aybu.core.models import populate
from aybu.core.models import engine_from_config_parser, create_session
from aybu.core.utils.request import Request as AybuRequest
from aybu.website.models import Base
from sqlalchemy.orm import Session

def read_config():
    parser = ConfigParser.ConfigParser()
    ini = os.path.realpath(
            os.path.join(os.path.dirname(__file__),
                "..",
                'tests.ini'))

    try:
        with open(ini) as f:
            parser.readfp(f)

    except IOError:
        raise Exception("Cannot find configuration file '%s'" % ini)
    return parser


def read_data():
    databag = os.path.realpath(
                os.path.join(
                        os.path.dirname(__file__),
                        "..", "data", "tests_data.json"))
    try:
        with open(databag) as f:
            return json.loads(f.read())

    except IOError:
        raise Exception("Cannot find data file '%s'" % databag)


class BaseTests(unittest.TestCase):

    def setUp(self):
        parser = read_config()
        self.engine = engine_from_config_parser(parser,
                                                'app:aybu-website')
        self.session = create_session(self.engine)
        AybuRequest.db_session = self.session
        AybuRequest.db_engine = self.engine
        self.req = AybuRequest({})
        self.ctx = testing.DummyResource()
        self.config = testing.setUp(request=self.req)
        self.req.registry = self.config.registry

    def tearDown(self):
        self.session.remove()
        Session.close_all()
        testing.tearDown()
        Base.metadata.drop_all(self.engine)



class FunctionalBase(unittest.TestCase):

    def setUp(self):
        from webtest import TestApp
        from aybu.website import main

        parser = read_config()
        data = read_data()
        section = 'app:aybu-website'
        populate(parser, data, section)

        settings = {opt: parser.get(section, opt)
                    for opt in parser.options(section)}
        app = main({}, **settings)
        self.testapp = TestApp(app)

    def tearDown(self):
        Session.close_all()