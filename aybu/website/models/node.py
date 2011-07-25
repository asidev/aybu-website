#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque
from logging import getLogger
from sqlalchemy import asc
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import UniqueConstraint
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import Table
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from aybu.website.models.base import Base
from aybu.website.models.language import Language


__all__ = ['Node', 'Menu', 'Page', 'Section', 'ExternalLink', 'InternalLink',
           'NodeInfo']


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
    def root(cls, weight=1):
        return Menu.query.filter(Menu.weight == weight).one()

    def __getitem__(self, lang):
        if isinstance(lang, Language):
            try:
                return NodeInfo.query.filter(NodeInfo.node == self).\
                                      filter(NodeInfo.lang == lang).one()
            except Exception as e:
                log.exception(e)

        raise KeyError(lang)

    @property
    def linked_by(self):
        return Node.query.filter(InternalLink.linked_to == self).all()

    @property
    def pages(self):
        return [p for p in self.crawl() if isinstance(p, Page)]

    def crawl(self, callback=None):
        queue = deque([self])
        visited = deque()
        while queue:
            parent = queue.popleft()
            if parent in visited:
                continue
            yield parent
            if callback:
                callback(parent)
            visited.append(parent)
            queue.extend(parent.children)

    @property
    def type(self):
        return self.__class__.__name__

    @property
    def path(self):
        """ Get all parents paths as a list
            i.e. with the tree A --> B --> C get_parents_path(C) returns [A, B]
        """
        n = self
        path = [self]
        while n.parent:
            n = n.parent
            path.insert(0, n)

        return path

    def __str__(self):
        return "<Node (%s) [id: %d, parent: %s, weigth:%d]>" % \
                (self.type, self.id, self.parent_id, self.weight)

    def __repr__(self):
        return self.__str__()


class NodeInfo(Base):

    __tablename__ = 'node_infos'

    id = Column(Integer, primary_key=True)
    label = Column(Unicode(64), nullable=False)
    title = Column(Unicode(64), default=None)
    url_part = Column(Unicode(64), default=None)

    # This field is very useful but denormalize the DB
    url = Column(Unicode(512), default=None)

    node_id = Column(Integer, ForeignKey('nodes.id',
                                         onupdate='cascade',
                                         ondelete='cascade'), nullable=False)

    node = relationship('Node', backref='translations')

    lang_id = Column(Integer, ForeignKey('languages.id',
                                         onupdate='cascade',
                                         ondelete='cascade'), nullable=False)

    lang = relationship('Language')

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
    links = relationship('NodeInfo', secondary=_links_table,
                         primaryjoin=id==_links_table.c.inverse_id,
                         secondaryjoin=id==_links_table.c.links_id)

    def __repr__(self):
        return "<NodeInfo [%d] '%s' %s>" % (self.id, self.label.encode('utf8'),
                                            self.url)
    @classmethod
    def get_by_url(cls, session, url):
        criterion = cls.url.ilike(url)
        return session.query(cls).filter(criterion).one()

    @classmethod
    def get_homepage(cls, session, language=None):

        query = session.query(cls).filter(cls.node.has(Page.home == True))

        if not language is None:
            query = query.filter(cls.lang == language)

        try:
            return query.one()

        except NoResultFound as e:
            log.debug(e)

        query = session.query(cls).filter(cls.lang == language)
        query = query.join(Page).order_by(asc(Page.id))

        home = query.first()
        home.node.home = True
        session.commit()

        return home


class Menu(Node):

    __mapper_args__ = {'polymorphic_identity': 'menu'}


node_banners = Table('nodes_banners__files',
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


class Page(Node):

    __mapper_args__ = {'polymorphic_identity': 'page'}

    home = Column(Boolean, default=False)
    sitemap_priority = Column(Integer, default=50, nullable=False)
    banners = relationship('Banner', secondary=node_banners)

    view_id = Column(Integer, ForeignKey('views.id',
                                         onupdate='cascade',
                                         ondelete='restrict'))#, nullable=False)
    view = relationship('View')


class Section(Node):

    __mapper_args__ = {'polymorphic_identity': 'section'}

    banners = relationship('Banner', secondary=node_banners)


class ExternalLink(Node):

    __mapper_args__ = {'polymorphic_identity': 'externallink'}

    # Maybe this should be removed from here cause it can change with language
    # ie: http://www.apple.com or http://www.apple.it
    url = Column(Unicode(512), default=None)


class InternalLink(Node):

    __mapper_args__ = {'polymorphic_identity': 'internallink'}

    linked_to_id = Column(Integer, ForeignKey('nodes.id',
                                              onupdate='cascade',
                                              ondelete='cascade'),)
#                          nullable=False)

    linked_to = relationship('Page', backref='linked_by', remote_side=Page.id,
                             primaryjoin='Page.id == InternalLink.linked_to_id')
