#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Copyright © 2010 Asidev s.r.l. - www.asidev.com """


from aybu.website.models.base import Base
from logging import getLogger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import Table
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship


__all__ = ['Theme']

log = getLogger(__name__)


class Theme(Base):

    __tablename__ = 'themes'
    __table_args__ = ({'mysql_engine': 'InnoDB'})

    name = Column(Unicode(128), primary_key=True)
    parent_name = Column(Unicode(128), ForeignKey('themes.name'))
    children = relationship('Theme',
                            backref=backref('parent', remote_side=name))
