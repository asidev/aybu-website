#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ©2010-present Asidev S.r.l. """

from aybu.website.lib.util import OrderedSet
from aybu.website.models.language import Language
from aybu.website.models.node import ExternalLink
from aybu.website.models.node import InternalLink
from aybu.website.models.node import Menu
from aybu.website.models.node import Page
from aybu.website.models.node import Section
from aybu.website.models.setting import Setting
from collections import deque
from collections import namedtuple
from recaptcha.client.captcha import displayhtml
from webhelpers.html.builder import literal
import logging
import re

__all__ = ['captcha', 'url', 'form_input', 'locale_from_language', 'urlfy',
           'static_url']

log = logging.getLogger(__name__)


CSS = namedtuple('CSS', ['href', 'media'])
JS = namedtuple('JS', ['href'])


class TemplateHelper(object):

    def __init__(self, request):
        self._request = request
        self._settings = SettingProxy(self._request.db_session)
        self._menus = MenuProxy(self._request.db_session)
        self._languages = Language.get_by_enabled(self._request.db_session,
                                                      True)
        self._translation = self._request.context
        node = getattr(self._translation, 'node', None)
        if not node is None:
            self._node = NodeProxy(node)
            self._language = getattr(self._request.context, 'lang', None)
        else:
            self._node = self._language = None


    def static_url(self, resource_url):
        if resource_url.startswith('/uploads'):
            return resource_url

        return str('/static%s' % resource_url)

    def url(self, url, *args, **kwargs):
        import inspect
        log.error("Called %s.url with params: '%s', '%s', '%s'",
                    __name__, url, args, kwargs)
        try:
            frame = inspect.stack()[1]
            log.error("Called from: %s'", frame)
            return url

        except Exception as e:
            log.debug('url helper does not work! %s', e)

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
        return 'dynamic'

    @property
    def user(self):
        return None

    @property
    def node(self):
        if self._node is None:
            raise ValueError('Node is None')

        return self._node

    @property
    def languages(self):
        return self._languages

    @property
    def lang(self):
        if self._language is None:
            raise ValueError('Language is None')

        return self._language

    @property
    def menus(self):
        return self._menus

    @property
    def translation(self):
        return self._translation

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

    def captcha(self, error=None):

        public_key = '6LeNHcYSAAAAAKHbUX4bGAE-DE_0fR_J0nynW1OR'

        html = displayhtml('6LeNHcYSAAAAAKHbUX4bGAE-DE_0fR_J0nynW1OR', error)

        return literal(html)


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


class MenuProxy(object):

    def __init__(self, session):
        self._menus = {}
        for menu in Menu.get_by_enabled(session, True):
            self._menus[menu.weight] = NodeProxy(menu)

    def __getitem__(self, weight):
        return self._menus[weight]


class NodeProxy(object):

    def __init__(self, node):

        if node is None:
            raise ValueError('node cannot be None')

        self._node = node

        self._translations = {}
        for translation in getattr(self._node, 'translations', []):
            self._translations[translation.lang] = translation

        self._children = [NodeProxy(children)
                          for children in getattr(self._node, 'children', [])]

    def __getitem__(self, language):
        try:
            return NodeInfoProxy(self._translations[language], self)
        except Exception as e:
            log.debug('Exception type: %s', e.__class__.__name__)
            log.debug('Node: %s', self._node)
            log.debug('Translations: %s', self._translations)
            log.debug('Language: %s', language)
            raise e

    """
    FOLLOWING FUNCTIONS are NOT USED... I think because there are bugs.
    """

    @property
    def linked_by(self):
        return Node.query.filter(InternalLink.linked_to == self).all()

    @property
    def pages(self):
        return [p for p in self.crawl() if issubclass(p.type, Page)]

    def crawl(self, callback=None):
        queue = deque([self._node])
        visited = deque()
        while queue:
            parent = queue.popleft()
            if parent in visited:
                continue
            if parent is None:
                continue
            yield NodeProxy(parent)
            if callback:
                callback(parent)
            visited.append(parent)
            queue.extend(parent.children)

    @property
    def type(self):
        return self._node.__class__

    @property
    def path(self):
        """ Get all parents paths as a list
            i.e. with the tree A --> B --> C get_parents_path(C) returns [A, B]
        """
        n = NodeProxy(self._node)
        path = [n]
        while n.parent:
            n = n.parent
            path.insert(0, n)

        return path

    @property
    def enabled(self):
        return getattr(self._node, 'enabled', None)

    @property
    def parent(self):
        if self._node.parent is None:
            return None
        return NodeProxy(self._node.parent)

    @property
    def banners(self):
        return self._node.banners

    @property
    def children(self):
        return self._children


class NodeInfoProxy(object):

    def __init__(self, info, node_proxy):

        if info is None:
            raise ValueError('node cannot be None')

        self._info = info
        self._node = node_proxy

    @property
    def node(self):
        return self._info.node

    @property
    def title(self):
        return self._info.title

    @property
    def label(self):
        return self._info.label

    @property
    def lang(self):
        return self._info.lang

    @property
    def url(self):
        if isinstance(self._info.node, Page):
            return self._info.url
        elif isinstance(self._info.node, (Menu, Section)):
            return None
        elif isinstance(self._info.node, InternalLink):
            return NodeProxy(self.node.linked_to)[self.lang].url
        elif isinstance(self._info.node, ExternalLink):
            return self.node.url
        raise TypeException('Cannot identify NodeInfo type!')
