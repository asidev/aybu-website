#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

        from aybu.website.models.base import Base
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session
        from sqlalchemy.orm import sessionmaker

        self.engine = create_engine('sqlite:///:memory:')
        self.session = scoped_session(sessionmaker())
        self.session.configure(bind=self.engine)

        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)


    def tearDown(self):
        self.session.remove()
        testing.tearDown()


class LanguageModelTest(ModelsTests):

    def test_constructor(self):
        from aybu.website.models.language import Language
        language = Language(id=1, lang=u'IT', country=u'it', enabled=True)

        self.assertEqual(language.id, 1)
        self.assertEqual(language.lang, u'it')
        self.assertEqual(language.country, u'IT')
        self.assertEqual(language.enabled, True)

    def test_get_by_lang(self):
        pass

    def test_get_by_enabled(self):
        pass

    def test_locale(self):
        pass

    def test_locales(self):
        pass

    def test_get_locales(self):
        pass
