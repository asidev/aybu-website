#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import UniqueConstraint
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
    home = Column(Boolean, default=False)
    weight = Column(Integer, nullable=False)

    parent_id = Column(Integer, ForeignKey('nodes.id'))
    children = relationship('Node',
                            backref=backref('parent', remote_side=id))

    #banners = ManyToMany('Banner')
    #translations = OneToMany('NodeInfo', cascade="all")
    #sitemap_priority = Field(Integer, default=50, required=True)



