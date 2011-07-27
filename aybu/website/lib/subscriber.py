#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.website.lib.helper import TemplateHelper

def add_renderer_globals(event):
    h = TemplateHelper(event['request'])
    event['_'] = event['request'].translate
    event['localizer'] = event['request'].localizer
    event['h'] = h
    event['c'] = h
    event['url'] = event['h'].url
    event['css_link'] = h.link_css
    event['js_link'] = h.link_js
    event['keywords'] = h.keywords

