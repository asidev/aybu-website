#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.website.lib.helper import Helper

def add_renderer_globals(event):
    event['_'] = event['request'].translate
    event['localizer'] = event['request'].localizer
    event['h'] = Helper()

