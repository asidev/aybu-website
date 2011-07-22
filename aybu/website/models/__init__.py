#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger
from sqlalchemy.ext.declarative import declarative_base


__all__ = []


log = getLogger(__name__)


Base = declarative_base()
