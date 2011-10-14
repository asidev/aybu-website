#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010 Asidev s.r.l.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from aybu.core.models import PageInfo
from aybu.website.lib.language import get_negotiated_language
from aybu.website.lib.contact_utils import handle_contact_form
from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.httpexceptions import HTTPTemporaryRedirect
from pyramid.renderers import render_to_response


def show_page(context, request):
    # FIXME: add query options to eager load: NodeInfo.Node.View.
    return render_to_response(context.node.view.fs_view_path,
                              {'page': context},
                              request=request)

def contact_post(context, request):
    return handle_contact_form(request)

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
