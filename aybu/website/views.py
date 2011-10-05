#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.website.models import PageInfo
from aybu.website.lib.language import get_negotiated_language
from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.httpexceptions import HTTPTemporaryRedirect
from pyramid.renderers import render_to_response


def show_page(context, request):
    # FIXME: add query options to eager load: NodeInfo.Node.View.
    return render_to_response(context.node.view.fs_view_path,
                              {'page': context},
                              request=request)

def favicon(request):
    raise HTTPMovedPermanently('/static/favicon.ico')


def sitemap(context, request):
    request.response.content_type = "text/xml"
    return {}


def robots(context, request):
    request.response.content_type='text/plain'
    return {}


def show_not_found_error(context, request):
    return {}


def choose_default_language(context, request):
    lang = get_negotiated_language(request)
    raise HTTPTemporaryRedirect(location='/%s' % (lang.lang))


def redirect_to_homepage(context, request):
    lang = get_negotiated_language(request)
    page = PageInfo.get_homepage(request.db_session, lang)
    raise HTTPMovedPermanently(location=page.url)
