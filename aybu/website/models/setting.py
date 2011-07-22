#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Copyright © 2010 Asidev s.r.l. - www.asidev.com """

from aybu.website.models.base import Base
from logging import getLogger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import String
from sqlalchemy.orm import relationship


__all__ = ['Setting', 'SettingType']

log = getLogger(__name__)


class SettingType(Base):

    __tablename__ = 'setting_types'
    __table_args__ = ({'mysql_engine': 'InnoDB'})

    name = Column(Unicode(64), primary_key=True)

    def __repr__(self):
        return "<SettingType %s>" % (self.name)


class Setting(Base):

    __tablename__ = 'settings'
    __table_args__ = ({'mysql_engine': 'InnoDB'})

    name = Column(Unicode(128), primary_key=True)
    value = Column(Unicode(512), nullable=False)
    raw_type = Column(String(8), nullable=False)
    ui_administrable = Column(Boolean, default=False)

    type_name = Column(Integer, ForeignKey('setting_types.name',
                                           onupdate='cascade',
                                           ondelete='restrict'))

    type = relationship('SettingType', backref='settings')

    def __repr__(self):
        return "<Setting %s (%s)>" % (self.name, self.raw_type)
