#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.httpexceptions import HTTPTemporaryRedirect
from pyramid.response import Response
import os


def show_page(context, request):
    return {'entity': context}


def favicon(context, request):
    # FIX THE PATH!!!
    _here = os.path.dirname(__file__)
    return Response(content_type='image/x-icon',
                    body=open(os.path.join(_here,
                                           'static', 'favicon.ico')).read())


def sitemap(context, request):
    return dict()


def robots(context, request):
    # FIX THE PATH!!!
    _here = os.path.dirname(__file__)
    return Response(content_type='text/plain',
                    body=open(os.path.join(_here,
                                           'static', 'robots.txt')).read())


def show_not_found_error(context, request):
    raise Exception(type(context))
    return dict()


def choose_default_language(context, request):
    location = '/it'
    raise HTTPTemporaryRedirect(location=location)


def redirect_to_homepage(context, request):
    location = '/%s/index.html' % context.lang
    raise HTTPMovedPermanently(location=location)
