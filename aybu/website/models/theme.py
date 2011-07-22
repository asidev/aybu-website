#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""


from elixir import using_options_defaults
from elixir import options_defaults
from elixir import Entity, Field, Unicode
from elixir import using_options
from elixir import ManyToOne, OneToMany, ManyToMany

from aybu.cms.lib.containers import Storage
from aybu.cms.model.file import File, Image, Banner
from aybu.cms.model.types import SHA1
from aybu.cms.model.language import Language
from aybu.cms.model.setting import SettingType, Setting
from aybu.cms.model.user import User, Group
from aybu.cms.model.view import View, ViewDescription
from aybu.cms.model.graph import NodeInfo, Page,\
                                   Section, ExternalLink, InternalLink,\
                                   Node, Menu

using_options_defaults(table_options=dict(mysql_engine="InnoDB"))
options_defaults.update(dict(table_options=dict(mysql_engine="InnoDB")))

__all__ = [
    'Language', 'Setting', 'User', 'View',
    'File', 'Image', 'Banner', 'SHA1', 'Keyword',
    'SettingType', 'Group', 'ViewDescription', 'Keyword', 'NodeInfo',
    'Page', 'Section', 'ExternalLink', 'InternalLink', 'Node', 'Menu'
]


class Keyword(Entity):
    name = Field(Unicode(64), primary_key=True)
    used_in = ManyToMany("NodeInfo",
                         tablename="node_infos_keywords",
                         table_kwargs=dict(useexisting=True),
                         onupdate="cascade", ondelete="cascade")

    using_options(tablename='keywords')

    def __str__(self):
        return "<Keyword %s>" % (self.name)

    def __repr__(self):
        return self.__str__()


class Theme(Entity):
    name = Field(Unicode(128), primary_key=True)
    children = OneToMany('Theme')
    # set cascade to "save-update" (the default is "save-update, merge", thus
    # disabling the merge cascade which saves us one query while merging theme
    # back from cache. Parent will be lazy loaded on access.
    parent = ManyToOne('Theme', colname="parent_name", cascade="save-update",
                       lazy=False)

    using_options(tablename='themes')

    def __str__(self):
        return "<Theme '%s'>" % (self.name)

    def __repr__(self):
        if self.parent:
            return "<Theme '%s' (parent: %s)>" % (self.name, self.parent.name)
        else:
            return "<Theme '%s' (top-level)>" % (self.name)

    def to_storage(self, children=True):
        s = Storage(self.to_dict())
        s.parent = self.parent.\
                   to_storage(children=False) if self.parent else None
        if children:
                s.children = [c.to_storage() for c in self.children]
        return s
