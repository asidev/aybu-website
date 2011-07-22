#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import UniqueConstraint
from sqlalchemy import Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship


__all__ = []


log = getLogger(__name__)


Base = declarative_base()


class Node(Base):

    __tablename__ = 'nodes'
    __table_args__ = (UniqueConstraint('parent_id', 'weight'),
                      {'mysql_engine': 'InnoDB'})

    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean, default=True)
    hidden = Column(Boolean, default=False)
    weight = Column(Integer, nullable=False)

    parent_id = Column(Integer, ForeignKey('nodes.id'))
    children = relationship('Node',
                            backref=backref('parent', remote_side=id))

    discriminator = Column('type', Unicode(50))
    __mapper_args__ = {'polymorphic_on': discriminator}
    #translations = OneToMany('NodeInfo', cascade="all")


class NodeInfo(Base):

    id = Column(Integer, primary_key=True)
    label = Column(Unicode(64), nullable=False)
    title = Column(Unicode(64), default=None)
    url_part = Column(Unicode(64), default=None)
    
    # This field is very useful but denormalize the DB
    computed_url = Column(Unicode(256), default=None)
    
    node = ManyToOne('Node', onupdate='cascade', ondelete='cascade',
                         colname='node_id', required=True)
    lang = ManyToOne("Language", colname="lang_id",
                     onupdate='cascade', ondelete='cascade', required=True)

    keywords = ManyToMany("Keyword",
                          tablename="node_infos_keywords",
                          table_kwargs=dict(useexisting=True),
                          onupdate="cascade", ondelete="cascade")

    meta_description = Column(UnicodeText(), default=u'')
    head_content = Column(UnicodeText(), default=u'')
    content = Column(UnicodeText(), default=u'')

    files = ManyToMany('File')
    images = ManyToMany('Image')
    links = ManyToMany('NodeInfo', onupdate="cascade", ondelete="cascade")

    using_options(tablename='node_infos')


class Menu(Node):
    __mapper_args__ = {'polymorphic_identity': 'menu'}


class Page(Node):
    __mapper_args__ = {'polymorphic_identity': 'page'}
    home = Column(Boolean, default=False)
    sitemap_priority = Column(Integer, default=50, nullable=False)
    #banners = ManyToMany('Banner')
    view = ManyToOne("View", onupdate='cascade', ondelete='restrict')


class Section(Node):
    __mapper_args__ = {'polymorphic_identity': 'section'}
    #banners = ManyToMany('Banner')


class ExternalLink(Node):
    __mapper_args__ = {'polymorphic_identity': 'externallink'}
    url = Field(Unicode(512), default=None)


class InternalLink(Node):
    __mapper_args__ = {'polymorphic_identity': 'internallink'}
    linked_to = ManyToOne("Page", colname="linked_to_id",
                          ondelete="cascade", onupdate="cascade")
    