#!/usr/bin/env python
# -*- coding: utf-8 -*-

from babel import Locale
import locale
from logging import getLogger
from pyramid.request import Request as BaseRequest
from pyramid.i18n import get_localizer, TranslationStringFactory
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session


__all__ = []
log = getLogger(__name__)


class Request(BaseRequest):

    db_engine = None
    db_session = None

    def __init__(self, *args, **kwargs):

        super(Request, self).__init__(*args, **kwargs)

        self.db_session = scoped_session(sessionmaker())

        if not self.db_engine is None:
            self.db_session.configure(bind=self.db_engine)

        self.add_finished_callback(self.finished_callback)

        # i18n support
        # http://docs.pylonsproject.org/projects/pyramid_cookbook/dev/i18n.html
        self.translation_factory = TranslationStringFactory('aybu-website')

        self._languages = self.accept_language.best_matches()
        self._locale_name = None
        self._language = None

    @classmethod
    def set_db_engine(cls, engine):

        if isinstance(engine, basestring):
            engine = create_engine(engine)

        cls.db_engine = engine

    @property
    def locale_name(self):
        # i18n support
        # http://docs.pylonsproject.org/projects/pyramid_cookbook/dev/i18n.html

        if not self._locale_name is None:
            return self._locale_name

        for locale in self.accepted_locales:
            return str(locale)

    @locale_name.setter
    def locale_name(self, locale_name):
        # i18n support
        # http://docs.pylonsproject.org/projects/pyramid_cookbook/dev/i18n.html
        self._locale_name = locale_name
        log.debug('Set request.locale_name: %s', self._locale_name)
        self.localizer = get_localizer(self)
        log.debug('Set request.localizer: %s', self.localizer)
        log.debug('Set locale: %s.UTF8', self._locale_name)
        locale.setlocale(locale.LC_ALL, '%s.UTF8' % self._locale_name)

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, language):
        log.debug('Set language: %s', language)
        self._language = language
        self.locale_name = str(language.locale)

    @property
    def languages(self):

        for language in self._languages:
            yield language

            language = language[:2]
            if language not in self._languages:
                yield language

    @property
    def accepted_locales(self):
        for language in self.languages:
            sep = '-' if '-' in language else '_'
            try:
                yield Locale.parse(language, sep)

            except Exception as e:
                log.debug(e)

    def translate(self, string):
        """ This function will be exported to templates as '_' """
        return self.localizer.translate(self.translation_factory(string))

    def finished_callback(self, request):
        """ It clears the database session. """
        self.db_session.remove()
        self.db_session.close()
