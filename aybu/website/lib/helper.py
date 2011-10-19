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

from aybu.core.utils.modifiers import urlify
from aybu.core.models import Language
from aybu.core.models import InternalLink, Node, Menu, Page, Section
from aybu.core.models import ExternalLink
from aybu.core.models import Setting
from collections import deque
from collections import namedtuple
from recaptcha.client.captcha import displayhtml
from webhelpers.html.builder import literal
import logging
import ast

log = logging.getLogger(__name__)


CSS = namedtuple('CSS', ['href', 'media'])
JS = namedtuple('JS', ['href'])

class NodeNotFound(object):
    """ A class mocking a translation when no translations
        are found for a given url (i.e. in 404)
    """
    def __init__(self, request):
        self.meta_description = ''
        self.parent = request.db_session.query(Menu).first()
        self.banners = []
        self.lang = request.language
        self.translations = [self]
        self.title = 'Pagina Non Trovata'
        self.head_content = ''
        self.id = -1
        self.node = self
        self.children = []


class TemplateHelper(object):

    def __init__(self, request):
        self._request = request
        self._settings = SettingProxy(self._request.db_session)
        self._menus = MenuProxy(self._request.db_session)
        self._languages = Language.get_by_enabled(self._request.db_session,
                                                      True)
        if hasattr(self._request, "context"):
            self._translation = self._request.context
            node = getattr(self._translation, 'node', None)
            if not node is None:
                self._node = NodeProxy(node)
                self._language = getattr(self._request.context, 'lang', None)
            else:
                self._node = self._language = None
        else:
            self._translation = NodeNotFound(request)
            self._node = NodeProxy(self._translation)
            self._language = request.language

    def static_url(self, resource_url):
        return str('/static%s' % resource_url)

    def url(self, url, *args, **kwargs):
        import inspect
        log.debug("Called %s.url with params: '%s', '%s', '%s'",
                    __name__, url, args, kwargs)
        try:
            frame = inspect.stack()[1]
            log.debug("Called from: %s'", frame)
            return url

        except Exception as e:
            log.error('url helper does not work! %s', e)

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
        return urlify(name)

    def captcha(self, error=None):

        #public_key = '6LeNHcYSAAAAAKHbUX4bGAE-DE_0fR_J0nynW1OR'

        html = displayhtml('6LeNHcYSAAAAAKHbUX4bGAE-DE_0fR_J0nynW1OR', error)

        return literal(html)


class SettingProxy(object):

    def __init__(self, session):
        self._settings = {}
        for setting in Setting.get_all(session):

            raw_type = setting.type.raw_type
            value = setting.value

            if raw_type != "unicode":
                if raw_type == "bool":
                    value = ast.literal_eval(str(setting.value))
                else:
                    value = eval(raw_type)(setting.value)

            self._settings[setting.name] = setting
            self._settings[setting.name].value = value

    def __getattr__(self, attr_name):

        if not attr_name in self._settings:
            raise AttributeError("Setting '%s' doesn't exist!" % attr_name)

        return self._settings[attr_name].value

    def __getitem__(self, attr_name):
        return getattr(self, attr_name)


class MenuProxy(object):

    def __init__(self, session):
        self._menus = []
        for menu in Menu.get_by_enabled(session, True):
            self._menus.insert(menu.weight - 1, NodeProxy(menu))

    def __getitem__(self, weight):
        return self._menus[weight - 1]


class NodeProxy(object):

    def __init__(self, node):

        if node is None:
            raise ValueError('node cannot be None')

        self._node = node

        self._translations = getattr(self._node, 'translations', [])
        self._translations_dict = {}
        for translation in self._translations:
            self._translations_dict[translation.lang] = translation

        self._children = [NodeProxy(child)
                          for child in getattr(self._node, 'children', [])]

    def __getitem__(self, language):
        try:
            return NodeInfoProxy(self._translations_dict[language], self)
        except Exception as e:
            log.debug('Exception type: %s', e.__class__.__name__)
            log.debug('Node: %s', self._node)
            log.debug('Translations: %s', self._translations)
            log.debug('Language: %s', language)
            raise e

    """
    FOLLOWING FUNCTIONS are NOT USED... I think because there are bugs.
    """

    def __eq__(self, node_proxy):
        if not isinstance(node_proxy, NodeProxy):
            raise Exception('Equivalence is allowed beetween NodeProxy object only')

        return True if self._node.id == node_proxy._node.id else False

    @property
    def sitemap_priority(self):
        return self._node.sitemap_priority

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
    def translations(self):
        return self._translations

    @property
    def banners(self):
        return self._node.banners

    @property
    def children(self):
        return self._children

    @property
    def linked_to(self):
        return self._node.linked_to

    @property
    def url(self):
        return self._node.url


class NodeInfoProxy(object):

    def __init__(self, info, node_proxy):

        if info is None:
            raise ValueError('info cannot be None')

        self._info = info
        self._node = node_proxy

    @property
    def node(self):
        return self._node

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
            return self._info.ext_url
        elif isinstance(self._info.node, NodeNotFound):
            return ''
        raise TypeError('Cannot identify NodeInfo type!')
