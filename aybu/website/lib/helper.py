#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010-2012 Asidev s.r.l.

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

import collections
from aybu.core.utils.modifiers import urlify
from aybu.core.models import Language
from aybu.core.models import (InternalLink,
                              Node,
                              Menu,
                              Page,
                              Section,
                              Banner,
                              Logo,
                              Background)
from aybu.core.models import ExternalLink
from aybu.core.models import Setting
from collections import deque
from collections import namedtuple
from recaptcha.client.captcha import displayhtml
from sqlalchemy.orm.exc import NoResultFound
from webhelpers.html.builder import literal
import logging


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

        self._rendering_type = 'dynamic'
        # old heka legacy. Remove ASAP
        self.section = None
        self.subsection = None
        self.page = None
        self.backgrounds = Background.all(request.db_session)

        if hasattr(self._request, "context"):
            self._translation = self._request.context
            node = getattr(self._translation, 'node', None)
            if not node is None:
                self._node = NodeProxy(node)
            else:
                self._node = None
        else:
            self._translation = NodeNotFound(request)
            self._node = NodeProxy(self._translation)

    def static_url(self, resource_url):
        return str('/static%s' % resource_url)

    @property
    def lang(self):
        return self._request.language

    @property
    def literal(self):
        return literal

    @property
    def settings(self):
        return self._settings

    @property
    def rendering_type(self):
        return self._rendering_type

    @rendering_type.setter
    def rendering_type(self, value):
        if value not in ('static', 'dynamic'):
            raise ValueError('Invalid rendering_type %s' % value)
        self._rendering_type = value

    @property
    def user(self):
        return self._request.user

    @property
    def node(self):
        if self._node is None:
            raise ValueError('Node is None')

        return self._node

    @node.setter
    def node(self, value):
        self._node = NodeProxy(value)

    @property
    def languages(self):
        return self._languages

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

    def _get_default(self, cls):
        session = self._request.db_session
        obj = cls.get_default(session)
        if obj:
            # remove obj from session so no query can be
            # issued by using it
            session.expunge(obj)
        return obj

    @property
    def default_banner(self):
        return self._get_default(Banner)

    @property
    def default_logo(self):
        default_logo = self._get_default(Logo)
        if not default_logo:
            default_logo = collections.namedtuple('Logo', ['url'])(url=None)
        return default_logo


class SettingProxy(object):

    def __init__(self, session):
        self.session = session
        self._settings = {}

    def __getattr__(self, attr_name):

        try:
            return self._settings[attr_name].value
        except KeyError:
            try:
                self._settings[attr_name] = Setting.get(self.session,
                                                        attr_name)
                return self._settings[attr_name].value
            except NoResultFound:
                msg = "Setting '%s' doesn't exist!" % attr_name
                log.error(msg)
                raise AttributeError(msg)

    def __getitem__(self, attr):
        return getattr(self, attr)


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
    def id(self):
        return self._node.id

    @property
    def home(self):
        return self._node.home

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
        elif isinstance(self._info.node, Section):
            if self._info.node.children:
                return self.node.children[0][self._info.lang]._info.url
            return None
        elif isinstance(self._info.node, Menu):
            return None
        elif isinstance(self._info.node, InternalLink):
            return NodeProxy(self.node.linked_to)[self.lang].url
        elif isinstance(self._info.node, ExternalLink):
            return self._info.ext_url
        elif isinstance(self._info.node, NodeNotFound):
            return ''
        raise TypeError('Cannot identify NodeInfo type!')
