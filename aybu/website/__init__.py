#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.website.request import Request
from aybu.website.models.base import Base
from aybu.website.resources import get_root_resource
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound


def main(global_config, **settings):

    engine = engine_from_config(settings, 'sqlalchemy.')
    # Set metadata for tables.
    Base.metadata.create_all(engine)
    # Set Engine in Request factory.
    # It is needed by Request objects to build Session.
    Request.set_db_engine(engine)

    config = Configurator(settings=settings, request_factory=Request)
    #config.add_subscriber(Request.set_default_language, NewRequest)

    # Initialize babel and Mako Internationalization
    """
    config.add_subscriber('aybu.website.subscribers.add_renderer_globals',
                          'pyramid.events.BeforeRender')
    config.add_subscriber(Request.add_localizer,
                          'pyramid.events.NewRequest')
    """
    config.add_translation_dirs('aybu.website:locale')

    config.include(add_routes)
    config.include(add_views)
    config.include(add_static_views)

    return config.make_wsgi_app()


def add_routes(config):

    config.add_route('favicon', '/favicon.ico')
    config.add_route('robots', '/robots.txt')
    config.add_route('sitemap', '/sitemap.xml')
    # Put URL dispatch configuration statements before Traversal ones!!!
    config.add_route('root', '/*traverse', factory=get_root_resource)


def add_views(config):

    # Views called after URL dispatch.

    config.add_view(route_name='favicon',
                    renderer='string',
                    view='aybu.website.views.favicon')

    config.add_view(route_name='robots',
                    renderer='string',
                    view='aybu.website.views.robots')

    config.add_view(route_name='sitemap',
                    renderer='string',
                    view='aybu.website.views.sitemap')

    # Views called after Traversal.

    config.add_view(route_name='root',
                    context='aybu.website.resources.NoLanguage',
                    renderer='aybu.website:templates/test.mako',
                    view='aybu.website.views.choose_default_language')

    config.add_view(route_name='root',
                    context='aybu.website.models.Language',
                    renderer='aybu.website:templates/test.mako',
                    view='aybu.website.views.redirect_to_homepage')

    config.add_view(route_name='root',
                    context='aybu.website.models.NodeInfo',
                    renderer='aybu.website:templates/test.mako',
                    view='aybu.website.views.show_page')

    config.add_view(route_name='root',
                    context=None,
                    renderer='aybu.website:templates/test.mako',
                    view='aybu.website.views.show_not_found_error')

    config.add_view(route_name='root',
                    context=NoResultFound,
                    renderer='aybu.website:templates/test.mako',
                    view='aybu.website.views.show_not_found_error')

    config.add_view(context=HTTPNotFound,
                    renderer='aybu.website:templates/test.mako',
                    view='aybu.website.views.show_not_found_error')



def add_static_views(config):

    config.add_static_view('static', 'aybu.website:static')

