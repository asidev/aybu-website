#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from pyramid.request import Request as BaseRequest
from pyramid.i18n import get_localizer, TranslationStringFactory


class Request(BaseRequest):

    db_engine = None
    db_session = None

    def __init__(self, *args, **kwargs):

        super(Request, self).__init__(*args, **kwargs)

        self.db_session = scoped_session(sessionmaker())

        if not self.db_engine is None:
            self.db_session.configure(bind=self.db_engine)

        self.lang = None
        self.add_finished_callback(self.finished_callback)

        # i18n support
        # http://docs.pylonsproject.org/projects/pyramid_cookbook/dev/i18n.html
        self.translation_factory = TranslationStringFactory('aybu-website')

        # parse headers for accepted langs
        self.languages = self.accept_language.best_matches()
        # threadlocal
        #self.set_language(self.registry.settings['default_locale_name'])

    @classmethod
    def set_db_engine(cls, engine):

        if isinstance(engine, basestring):
            engine = create_engine(engine)

        cls.db_engine = engine

    def translate(self, string):
        """ This function will be exported to templates as '_' """
        return self.localizer.translate(self.translation_factory(string))

    def finished_callback(self, request):
        """ It clears the database session. """
        self.db_session.remove()
        self.db_session.close()

    def set_language(self, lang):

        if not isinstance(lang, basestring):
            self.lang = lang
            lang = lang.lang

        self._LOCALE_ = lang
        self.localizer = get_localizer(self)

