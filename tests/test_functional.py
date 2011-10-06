
from . test_base import FunctionalBase


class TestWebsite(FunctionalBase):

    def test_redir(self):
        res = self.testapp.get('/', status=307)
