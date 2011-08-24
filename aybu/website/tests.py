#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from pyramid import testing
from logging import getLogger

from babel import Locale

from aybu.website.models.language import Language

log = getLogger(__name__)


"""
class ViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from aybu.website.views import my_view
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

        language = Language(id=1, lang=u'IT', country=u'it', enabled=True)

        self.assertEqual(language.id, 1)
        self.assertEqual(language.lang, u'it')
        self.assertEqual(language.country, u'IT')
        self.assertEqual(language.enabled, True)

    def test_eq(self):

        languages = []

        for enabled in (True, False):
            languages.append(Language(lang=u'it', country=u'it',
                                      enabled=enabled))
            languages.append(Language(lang=u'it', country=u'IT',
                                      enabled=enabled))
            languages.append(Language(lang=u'IT', country=u'IT',
                                      enabled=enabled))
            languages.append(Language(lang=u'IT', country=u'it',
                                      enabled=enabled))

        # Object are not added to session otherwise they cause integrity error

        for i in xrange(0, len(languages)):
            for j in xrange(i, len(languages)):
                self.assertEqual(languages[i], languages[j])


    def test_get_by_lang(self):

        languages = [
            Language(id=1, lang=u'it', country=u'IT', enabled=True),
            Language(id=2, lang=u'en', country=u'GB', enabled=True),
            Language(id=3, lang=u'es', country=u'ES', enabled=True),
            Language(id=4, lang=u'de', country=u'DE', enabled=False),
            Language(id=5, lang=u'fr', country=u'FR', enabled=False),
            Language(id=6, lang=u'ru', country=u'RU', enabled=False),
            Language(id=7, lang=u'zh', country=u'CN', enabled=False)
        ]

        for language in languages:
            self.session.add(language)


        self.session.commit()

        self.assertEqual(languages[0], Language.get_by_lang(self.session, u'it'))
        self.assertEqual(languages[0], Language.get_by_lang(self.session, u'IT'))
        self.assertNotEqual(languages[0], Language.get_by_lang(self.session, u'en'))
        self.assertNotEqual(languages[0], Language.get_by_lang(self.session, u'EN'))


    def test_get_by_enabled(self):

        languages = [
            Language(id=1, lang=u'it', country=u'IT', enabled=True),
            Language(id=2, lang=u'en', country=u'GB', enabled=True),
            Language(id=3, lang=u'es', country=u'ES', enabled=True),
            Language(id=4, lang=u'de', country=u'DE', enabled=False),
            Language(id=5, lang=u'fr', country=u'FR', enabled=False),
            Language(id=6, lang=u'ru', country=u'RU', enabled=False),
            Language(id=7, lang=u'zh', country=u'CN', enabled=False)
        ]

        for language in languages:
            self.session.add(language)

        self.session.commit()

        enabled = Language.get_by_enabled(self.session, True)
        disabled  = Language.get_by_enabled(self.session, False)
        all = Language.get_by_enabled(self.session)

        for i in xrange(0,3):
            self.assertIn(languages[i], enabled)
            self.assertIn(languages[i], all)
            self.assertNotIn(languages[i], disabled)

        for i in xrange(3,7):
            self.assertIn(languages[i], disabled)
            self.assertIn(languages[i], all)
            self.assertNotIn(languages[i], enabled)

    def test_locale(self):
        l = Language(id=1, lang=u'it', country=u'IT', enabled=True)

        self.assertEqual(Locale(u'it', u'IT'), l.locale)


    def test_locales(self):
        l = Language(id=1, lang=u'it', country=u'IT', enabled=True)

        locales = []
        for locale in l.locales:
            locales.append(locale)

        self.assertIn(Locale(u'it', u'IT'), locales)
        self.assertIn(Locale(u'it'), locales)

    def test_get_locales(self):
        languages = [
            Language(id=1, lang=u'it', country=u'IT', enabled=True),
            Language(id=2, lang=u'en', country=u'GB', enabled=True),
            Language(id=3, lang=u'es', country=u'ES', enabled=True),
            Language(id=4, lang=u'de', country=u'DE', enabled=False),
            Language(id=5, lang=u'fr', country=u'FR', enabled=False),
            Language(id=6, lang=u'ru', country=u'RU', enabled=False),
            Language(id=7, lang=u'zh', country=u'CN', enabled=False)
        ]

        for language in languages:
            self.session.add(language)

        self.session.commit()

        enabled_locales = []
        for language in Language.get_locales(self.session, enabled=True):
            enabled_locales.append(language)

        enabled_strict_locales = []
        for language in Language.get_locales(self.session, enabled=True, strict=True):
            enabled_strict_locales.append(language)

        disabled_locales = []
        for language in Language.get_locales(self.session, enabled=False):
            disabled_locales.append(language)

        disabled_strict_locales = []
        for language in Language.get_locales(self.session, enabled=False, strict=True):
            disabled_strict_locales.append(language)

        all_locales = []
        for language in Language.get_locales(self.session):
            all_locales.append(language)

        all_strict_locales = []
        for language in Language.get_locales(self.session, strict=True):
            all_strict_locales.append(language)

        for language in languages:
            full_locale = Locale(language.lang.lower(), language.country.upper())
            lang_locale = Locale(language.lang.lower())

            if language.enabled:
                self.assertIn(full_locale, enabled_locales)
                self.assertIn(lang_locale, enabled_locales)
                self.assertIn(full_locale, enabled_strict_locales)
                self.assertNotIn(lang_locale, enabled_strict_locales)
            else:
                self.assertIn(full_locale, disabled_locales)
                self.assertIn(lang_locale, disabled_locales)
                self.assertIn(full_locale, disabled_strict_locales)
                self.assertNotIn(lang_locale, disabled_strict_locales)


            self.assertIn(full_locale, all_locales)
            self.assertIn(lang_locale, all_locales)
            self.assertIn(full_locale, all_strict_locales)
            self.assertNotIn(lang_locale, all_strict_locales)


class PageModelTest(ModelsTests):

    def test_constructor(self):
        from aybu.website.models.node import Page

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
