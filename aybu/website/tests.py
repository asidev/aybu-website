import unittest

from pyramid import testing

"""
class ViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from aybuwebsite.views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['project'], 'aybu-website')
"""


class ModelsTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        from aybu.website.lib.database import create_session
        self.session = create_session(self.config)

    def tearDown(self):
        self.session.remove()
        testing.tearDown()


class LanguageModelTest(ModelsTests):

    def test_constructor(self):
        from aybu.website.models.language import Language
        language = Language(id=1, lang=u'it', country=u'it', enabled=True)

        self.assertEqual(language.id, 1)
        self.assertEqual(language.lang, u'it')
        self.assertEqual(language.country, u'IT')
        self.assertEqual(language.enabled, True)


