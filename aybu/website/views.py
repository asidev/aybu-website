#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.website.models import Language
from aybu.website.models import NodeInfo
from babel import Locale
from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPTemporaryRedirect
from pyramid.renderers import render_to_response
from pyramid.response import Response
from sqlalchemy.orm.exc import NoResultFound
import os


def show_page(context, request):
    # FIXME: add query options to eager load: NodeInfo.Node.View.
    return render_to_response(context.node.view.fs_view_path,
                              {'page': context},
                              request=request)


def favicon(context, request):
    favicon = os.path.join(request.registry.settings['instance_uploads_dir'],
                           'favicon.ico')
    try:
        icon = open(favicon)
        return Response(content_type='image/x-icon', app_iter=icon)
    except IOError:
        raise NotFound()


def sitemap(context, request):
    def add_content_type(request, response):
        response.content_type='text/xml'

    request.add_response_callback(add_content_type)
    return {}


def robots(context, request):
    def add_content_type(request, response):
        response.content_type='text/plain'

    request.add_response_callback(add_content_type)
    return {}


def show_not_found_error(context, request):
    return {}


def choose_default_language(context, request):

    # Get all the registered and enabled languages of the system.
    available = [str(locale)
                 for locale in Language.get_locales(request.db_session,
                                                    enabled=True)]

    # Get client preferred languages.
    preferred = [str(locale) for locale in request.accepted_locales]

    # Choose the best one.
    negotiated = Locale.negotiate(preferred, available)

    location = '/%s'

    if not negotiated is None:
        location = location % negotiated.language

    else:
        location = location % available[0]

    raise HTTPTemporaryRedirect(location=location)


def redirect_to_homepage(context, request):
    # Search the homepage translated in the language specified by context.
    page = NodeInfo.get_homepage(request.db_session, context)

    if page is None:
        raise HTTPNotFound('There is no homepage.')

    raise HTTPMovedPermanently(location=page.url)
