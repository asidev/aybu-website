import unittest
import ConfigParser
import os

from pyramid import testing
from aybu.core.models import engine_from_config_parser, create_session
from aybu.core.utils.request import Request as AybuRequest
from aybu.website.models import Base

class AugmentedRequest(testing.DummyRequest, AybuRequest):
    pass

class BaseTests(unittest.TestCase):

    def setUp(self):
        self.req = testing.DummyRequest()
        self.ctx = testing.DummyResource()
        self.config = testing.setUp(request=self.req)

    def tearDown(self):
        testing.tearDown()

    def setup_model(self):
        self.config = ConfigParser.ConfigParser()
        ini = os.path.realpath(
                os.path.join(os.path.dirname(__file__),
                    "..",
                    'tests.ini'))

        try:
            with open(ini) as f:
                self.config.readfp(f)

        except IOError:
            raise Exception("Cannot find configuration file '%s'" % ini)

        self.engine = engine_from_config_parser(self.config)
        self.session = create_session(self.engine)
        Base.metadata.create_all(self.engine)
        AybuRequest.db_session = self.session
        AybuRequest.db_engine = self.engine
        self.req = AybuRequest({})
