#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger
from sqlalchemy import and_
from sqlalchemy import asc
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import UniqueConstraint
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import aliased
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.sql import func

from aybu.website.models.base import Base
from aybu.website.models.base import get_sliced
from aybu.website.models.language import Language


__all__ = ['Node', 'Menu', 'Page', 'Section', 'ExternalLink', 'InternalLink',
           'NodeTranslation', 'MenuTranslation', 'PageTranslation', 
           'SectionTranslation', 'ExternalLinkTranslation', 
           'InternalLinkTranslation', 'Keyword']


log = getLogger(__name__)


class Node(Base):

    __tablename__ = 'nodes'
    __table_args__ = (UniqueConstraint('parent_id', 'weight'),
                      {'mysql_engine': 'InnoDB'})

    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean, default=True)
    hidden = Column(Boolean, default=False)
    weight = Column(Integer, nullable=False)

    parent_id = Column(Integer, ForeignKey('nodes.id'))
    children = relationship('Node', backref=backref('parent', remote_side=id),
                            primaryjoin='Node.id == Node.parent_id')

    discriminator = Column('row_type', Unicode(50))
    __mapper_args__ = {'polymorphic_on': discriminator}

    @classmethod
    def get_by_enabled(cls, session, enabled=None, start=None, limit=None):

        query = session.query(cls)

        if not enabled is None:
            query = query.filter(cls.enabled == enabled)

        return get_sliced(query, start, limit)

    def __repr__(self):
        return "<Node (%s) [id: %d, parent: %s, weigth:%d]>" % \
                (self.__class__.__name__, self.id, self.parent_id, self.weight)

    @hybrid_property
    def translations(self):
        return self.translations_by_language

    @property
    def translations_by_language(self):

        if getattr(self, '_translations_by_language', None) is None:
            self._translations_by_language = {}

        for translation in self._translations:
            self._translations_by_language[translation.lang] = translation

        return self._translations_by_language


class NodeTranslation(Base):

    __tablename__ = 'node_infos'

    id = Column(Integer, primary_key=True)
    label = Column(Unicode(64), nullable=False)
    url_part = Column(Unicode(64), default=None)
    # This field is very useful but denormalize the DB
    url = Column(Unicode(512), default=None)

    discriminator = Column('row_type', Unicode(50))
    __mapper_args__ = {'polymorphic_on': discriminator}

    node_id = Column(Integer, ForeignKey('nodes.id',
                                         onupdate='cascade',
                                         ondelete='cascade'), nullable=False)

    #node = relationship('Node', backref='translations')

    lang_id = Column(Integer, ForeignKey('languages.id',
                                         onupdate='cascade',
                                         ondelete='cascade'), nullable=False)

    lang = relationship('Language')

    def __repr__(self):
        url = '' if self.url is None else self.url

        return "<%s [%d] '%s' %s>" % (self.__class__.__name__,
                                      self.id,
                                      self.label.encode('utf8'),
                                      url.encode('utf8'))

    @declared_attr
    def node(cls):
        # Follow the convention: Node -> {Node}Translation
        class_ = cls.__name__.replace('Translation', '')
        return relationship(class_,
                            backref='_translations',
                            primaryjoin='%s.id==%s.node_id' % (class_,
                                                               cls.__name__))

    @classmethod
    def get_by_url(cls, session, url):
        criterion = cls.url.ilike(url)
        return session.query(cls).filter(criterion).one()


class Menu(Node):

    __mapper_args__ = {'polymorphic_identity': 'menu'}


class MenuTranslation(NodeTranslation):

    __mapper_args__ = {'polymorphic_identity': 'menutranslation'}


class Keyword(Base):

    __tablename__ = 'keywords'
    __table_args__ = ({'mysql_engine': 'InnoDB'})

    name = Column(Unicode(64), primary_key=True)


class Section(Node):

    __mapper_args__ = {'polymorphic_identity': 'section'}

    @declared_attr
    def keywords(cls):
        _keywords_table = Table('node_infos__keywords',
                                Base.metadata,
                                Column('node_infos_id',
                                       Integer,
                                       ForeignKey('node_infos.id',
                                                  onupdate="cascade",
                                                  ondelete="cascade")),
                                       Column('keyword_name',
                                              Unicode(64),
                                              ForeignKey('keywords.name',
                                                         onupdate="cascade",
                                                         ondelete="cascade")))
        return relationship('Keyword', secondary=_keywords_table,
                            primaryjoin=cls.id==_keywords_table.c.node_infos_id,
                            secondaryjoin=Keyword.name==_keywords_table.c.keyword_name)

    @declared_attr
    def banners(cls):
        _banners_table = Table('nodes_banners__files',
                               Base.metadata,
                               Column('nodes_id',
                                      Integer,
                                      ForeignKey('nodes.id',
                                                 onupdate="cascade",
                                                 ondelete="cascade")),
                               Column('files_id',
                                      Integer,
                                      ForeignKey('files.id',
                                                 onupdate="cascade",
                                                 ondelete="cascade")))
        return relationship('Banner', secondary=_banners_table)


class SectionTranslation(NodeTranslation):

    __mapper_args__ = {'polymorphic_identity': 'sectiontranslation'}

    title = Column(Unicode(64), default=None)


class Page(Section):

    __mapper_args__ = {'polymorphic_identity': 'page'}

    home = Column(Boolean, default=False)
    sitemap_priority = Column(Integer, default=50, nullable=False)

    view_id = Column(Integer, ForeignKey('views.id',
                                         onupdate='cascade',
                                         ondelete='restrict'))#, nullable=False)
    view = relationship('View')


class PageTranslation(SectionTranslation):

    __mapper_args__ = {'polymorphic_identity': 'pagetranslation'}

    meta_description = Column(UnicodeText(), default=u'')
    head_content = Column(UnicodeText(), default=u'')
    content = Column(UnicodeText(), default=u'')

    _files_table = Table('node_infos_files__files',
                         Base.metadata,
                         Column('node_infos_id',
                                Integer,
                                ForeignKey('node_infos.id',
                                           onupdate="cascade",
                                           ondelete="cascade")),
                         Column('files_id',
                                Integer,
                                ForeignKey('files.id',
                                           onupdate="cascade",
                                           ondelete="cascade")))
    files = relationship('File', secondary=_files_table)

    _images_table = Table('node_infos_images__files',
                          Base.metadata,
                          Column('node_infos_id',
                                 Integer,
                                 ForeignKey('node_infos.id',
                                            onupdate="cascade",
                                            ondelete="cascade")),
                          Column('files_id',
                                 Integer,
                                 ForeignKey('files.id',
                                            onupdate="cascade",
                                            ondelete="cascade")))
    images = relationship('Image', secondary=_images_table)

    _links_table = Table('node_infos_links__node_infos',
                         Base.metadata,
                         Column('inverse_id',
                                Integer,
                                ForeignKey('node_infos.id',
                                           onupdate="cascade",
                                           ondelete="cascade")),
                         Column('links_id',
                                Integer,
                                ForeignKey('node_infos.id',
                                           onupdate="cascade",
                                           ondelete="cascade")))
    links = relationship('PageTranslation', secondary=_links_table,
                         primaryjoin=NodeTranslation.id==_links_table.c.inverse_id,
                         secondaryjoin=NodeTranslation.id==_links_table.c.links_id)

    @classmethod
    def get_homepage(cls, session, language=None):

        # Get the NodeTranslation which belongs to the 'home' Node.
        query = session.query(cls).filter(cls.node.has(Page.home == True))

        if not language is None:
            query = query.filter(cls.lang == language)

        try:
            return query.one()

        except NoResultFound as e:
            log.debug(e)

        # There is no node with home == True.
        # Get the NodeTranslation of the Page with min weight in the main Menu.
        query = session.query(func.min(Page.weight).label('min_weight'))
        criterion = Page.parent.has(and_(Menu.weight == 1,
                                         Menu.parent == None))
        query = query.filter(criterion).group_by(Page.weight)
        criterion = and_(Page.parent.has(and_(Menu.weight == 1,
                                              Menu.parent == None)),
                         Page.weight == query.subquery())
        query = session.query(Page).filter(criterion)
        page = aliased(Page, query.subquery())
        query = session.query(cls).filter(cls.lang == language)
        query = query.join(page, cls.node)

        home = query.first()
        if home is None:
            # The previous query is empty.
            # Get the NodeTranslation of the first inserted Page.
            query = session.query(cls).filter(cls.lang == language)
            query = query.join(Page).order_by(asc(Page.id))
            home = query.first()

        if not home is None:
            home.node.home = True
            session.commit()

        return home


class ExternalLink(Node):

    __mapper_args__ = {'polymorphic_identity': 'externallink'}

    # Maybe this should be removed from here cause it can change with language
    # ie: http://www.apple.com or http://www.apple.it
    # url = Column(Unicode(512), default=None)


class ExternalLinkTranslation(NodeTranslation):

    __mapper_args__ = {'polymorphic_identity': 'externallinktranslation'}


class InternalLink(Node):

    __mapper_args__ = {'polymorphic_identity': 'internallink'}

    linked_to_id = Column(Integer, ForeignKey('nodes.id',
                                              onupdate='cascade',
                                              ondelete='cascade'))

    linked_to = relationship('Page', backref='linked_by', remote_side=Page.id,
                             primaryjoin='Page.id == InternalLink.linked_to_id')


class InternalLinkTranslation(NodeTranslation):

    __mapper_args__ = {'polymorphic_identity': 'internallinktranslation'}

    @property
    def url(self):
        return self.node.linked_to.translations[self.lang].url
