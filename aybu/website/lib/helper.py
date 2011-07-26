#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ©2010-present Asidev S.r.l. """

from aybu.website.models.language import Language
from aybu.website.models.setting import Setting
from webhelpers.html.builder import literal
from captchalib.helper import captcha
import logging
import re

__all__ = ['captcha', 'url', 'form_input', 'locale_from_language', 'urlfy',
           'static_url']

log = logging.getLogger(__name__)


class Helper(object):

    def __init__(self, request):
        self._request = request
        self._css = []
        self._js = []
        self._settings = SettingProxy(self._request.db_session)
        self._node = getattr(self._request.context, 'node', None)
        self._language = getattr(self._request.context, 'lang', None)
        self._languages = Language.get_by_enabled(self._request.db_session,
                                                  True)
        self._menus = Menu.get_by_

    def url(self, url, *args, **kwargs):
        import inspect
        log.error("Called %s.url with params: '%s', '%s', '%s'",
                    __name__, url, args, kwargs)
        try:
            frame = inspect.stack()[1]
            log.error("Called from: %s'", frame)
            return url

        finally:
            del frame

    @property
    def literal(self):
        return literal

    @property
    def settings(self):
        return self._settings

    @property
    def rendering_type(self):
        return None

    @property
    def user(self):
        return None

    @property
    def node(self):
        return self._node

    @property
    def languages(self):
        return self._languages

    @property
    def lang(self):
        return self._language

    def urlify(self, name):

        xlate = {
            0xc0: 'A', 0xc1: 'A', 0xc2: 'A', 0xc3: 'A', 0xc4: 'A', 0xc5: 'A',
            0xc6: 'Ae', 0xc7: 'C',
            0xc8: 'E', 0xc9: 'E', 0xca: 'E', 0xcb: 'E',
            0xcc: 'I', 0xcd: 'I', 0xce: 'I', 0xcf: 'I',
            0xd1: 'N',
            0xd2: 'O', 0xd3: 'O', 0xd4: 'O', 0xd5: 'O', 0xd6: 'O',
            0xd9: 'U', 0xda: 'U', 0xdb: 'U', 0xdc: 'U',
            0xdd: 'Y',
            0xe0: 'a', 0xe1: 'a', 0xe2: 'a', 0xe3: 'a', 0xe4: 'a', 0xe5: 'a',
            0xe6: 'ae', 0xe7: 'c',
            0xe8: 'e', 0xe9: 'e', 0xea: 'e', 0xeb: 'e',
            0xec: 'i', 0xed: 'i', 0xee: 'i', 0xef: 'i',
            0xf1: 'n',
            0xf2: 'o', 0xf3: 'o', 0xf4: 'o', 0xf5: 'o', 0xf6: 'o',
            0xf9: 'u', 0xfa: 'u', 0xfb: 'u', 0xfc: 'u',
            0xfd: 'y', 0xff: 'y'
        }

        url = name.strip()

        pattern = "\s"
        compiled = re.compile(pattern)
        m = compiled.search(url)
        while m:
            url = "%s%s%s" % (url[:m.start()], '_', url[m.end():])
            m = compiled.search(url)

        for char in url:
            code = ord(char)
            if code in xlate:
                url = url.replace(char, xlate[code])

        pattern = "[^a-zA-Z0-9_]"
        compiled = re.compile(pattern)
        m = compiled.search(url)
        while m:
            url = "%s%s" % (url[:m.start()], url[m.end():])
            m = compiled.search(url)

        url = url.lower()
        url = url.strip('_')

        return url

    def static_url(self, resource_url):
        if resource_url.startswith('/uploads'):
            return resource_url

        return str('/static%s' % resource_url)

    def captcha(self, error=None):

        public_key = '6LeNHcYSAAAAAKHbUX4bGAE-DE_0fR_J0nynW1OR'

        html = displayhtml('6LeNHcYSAAAAAKHbUX4bGAE-DE_0fR_J0nynW1OR', error)

        return literal(html)

    def locale_from_language(self, language, language_only=False):
        from babel import Locale
        try:
            if language_only:
                locale = Locale(language.lang.lower(), language.country.upper())
            else:
                locale = Locale(language.lang.lower(), language.country.upper())
            return locale
        except Exception:
            if language_only:
                lang = '%s %s' % (language.lang.lower(), language.country.upper())
            else:
                lang = '%s' % (language.lang.lower())
            message = 'Unable to create locale using %s' % (lang)
            log.exception(message)
            raise Exception(message)


class SettingProxy(object):

    def __init__(self, session):
        self._settings = {}
        for setting in Setting.get_all(session):
            self._settings[setting.name] = setting

    def __getattr__(self, attr_name):

        if not attr_name in self._settings:
            raise AttributeError("Setting '%s' doesn't exist!" % attr_name)

        return self._settings[attr_name].value

    def __getitem__(self, attr_name):
        return getattr(self, attr_name)
