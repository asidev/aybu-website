#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

from logging import getLogger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import UniqueConstraint
from sqlalchemy import Unicode
from sqlalchemy.ext.declarative import declarative_base

__all__ = []


log = getLogger(__name__)


Base = declarative_base()


class Language(Base):

    __tablename__ = 'languages'
    __table_args__ = (UniqueConstraint('lang', 'country'),
                      {'mysql_engine': 'InnoDB'})

    id = Column(Integer, primary_key=True)
    lang = Column(Unicode(2), nullable=False)
    country = Column(Unicode(2), nullable=False)
    enabled = Column(Boolean, default=True)

    def __repr__(self):
        return "<Language %s_%s [%s]>" % (self.lang,
                                          self.country,
                                          "enabled" if self.\
                                                    enabled else "disabled")

    def __setattr__(self, attr, value):
        if attr == u"lang":
            value = value.lower()
        elif attr == u"country":
            value = value.upper()
        super(Language, self).__setattr__(attr, value)

    def __eq__(self, other):
        return self.lang == other.lang and self.country == other.country
