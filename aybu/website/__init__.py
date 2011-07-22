#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.website.request import Request
from aybu.website.models import Base
from aybu.website.resources import get_root_resource
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy import engine_from_config


def main(global_config, **settings):

    engine = engine_from_config(settings, 'sqlalchemy.')
    Base.metadata.create_all(engine)
    Request.set_db_engine(engine)

    config = Configurator(settings=settings)

    # initialize babel
    config.add_translation_dirs('aybu.website:locale')

    config.include(add_routes)
    config.include(add_views)
    config.include(add_static_views)

    return config.make_wsgi_app()


def add_routes(config):

    config.add_route('favicon', '/favicon.ico')
    config.add_route('robots', '/robots.txt')
    config.add_route('sitemap', '/sitemap.xml')
    config.add_route('root', '/*traverse', factory=get_root_resource)

    return config


def add_views(config):

    config.add_view(route_name='favicon',
                    renderer='string',
                    view='aybu.website.views.favicon')

    config.add_view(route_name='robots',
                    renderer='string',
                    view='aybu.website.views.robots')

    config.add_view(route_name='sitemap',
                    renderer='string',
                    view='aybu.website.views.sitemap')

    config.add_view(context='aybu.website.resources.NoLanguage',
                    renderer='aybu.website:templates/test.mako',
                    view='aybu.website.views.my_view')

    config.add_view(context=HTTPNotFound,
                    renderer='aybu.website:templates/test.mako',
                    view='aybu.website.views.show_not_found_error')

    return config


def add_static_views(config):

    config.add_static_view('static', 'aybu.website:static')

    return config
