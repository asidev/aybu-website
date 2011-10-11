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

from aybu.core.utils.request import Request
from aybu.core.models import Base, File, Image
from aybu.website.resources import get_root_resource
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy import engine_from_config
from sqlalchemy.ext.sqlsoup import SqlSoup
from sqlalchemy.orm.exc import NoResultFound
import logging
import os
import pkg_resources

__version__ = (0, 1, 0, "alpha", 1)
log = logging.getLogger(__name__)


def main(global_config, **settings):

    engine = engine_from_config(settings, 'sqlalchemy.')
    # Set metadata for tables.
    Base.metadata.create_all(engine)
    # Set Engine in Request factory.
    # It is needed by Request objects to build Session.
    Request.set_db_engine(engine)

    config = Configurator(settings=settings, request_factory=Request)

    # Initialize Babel translation dirs.
    config.add_translation_dirs('aybu.website:locale')

    config.include(add_subscribers)
    config.include(add_assets)
    config.include(add_routes)
    config.include(add_views)

    return config.make_wsgi_app()


def add_subscribers(config):

    config.add_subscriber('aybu.website.lib.subscriber.add_renderer_globals',
                          'pyramid.events.BeforeRender')


def add_routes(config):

    config.add_route('favicon', '/favicon.ico')
    config.add_route('robots', '/robots.txt')
    config.add_route('sitemap', '/sitemap.xml')

    # Put URL dispatch configuration statements before Traversal ones!!!
    config.add_route('root', '/*traverse', factory=get_root_resource)


def add_views(config):

    # Views called after URL dispatch.

    config.add_view(route_name='favicon', view='aybu.website.views.favicon')

    config.add_view(route_name='robots',
                    renderer='/base/robots.mako',
                    view='aybu.website.views.robots')

    config.add_view(route_name='sitemap',
                    renderer='/base/sitemap.mako',
                    view='aybu.website.views.sitemap')

    # Views called after Traversal.

    config.add_view(route_name='root',
                    context='aybu.website.resources.NoLanguage',
                    view='aybu.website.views.choose_default_language')

    config.add_view(route_name='root',
                    context='aybu.core.models.Language',
                    view='aybu.website.views.redirect_to_homepage')

    config.add_view(route_name='root',
                    context='aybu.core.models.NodeInfo',
                    view='aybu.website.views.show_page')

    config.add_view(route_name='root',
                    context=None,
                    renderer='/errors/404.mako',
                    view='aybu.website.views.show_not_found_error')

    config.add_view(route_name='root',
                    context=NoResultFound,
                    renderer='/errors/404.mako',
                    view='aybu.website.views.show_not_found_error')

    config.add_view(context=HTTPNotFound,
                    renderer='/errors/404.mako',
                    view='aybu.website.views.show_not_found_error')


def add_assets(config):
    """ Setup search paths for static files and for templates """

    # Use SqlSoup to access database to avoid requiring the entities to be
    # mapped, which is not the case when we are in a multiprocess environment.
    engine = engine_from_config(config.registry.settings, "sqlalchemy.")
    db = SqlSoup(engine)
    tname = db.settings.filter(db.settings.name == u'theme_name').one().value
    theme = db.themes.filter(db.themes.name == tname).one()

    log.info("Adding static view for aybu")
    #config.add_static_view('favicon.ico/', 'aybu.website:static/favicon.ico')
    config.add_static_view('static', 'aybu.website:static/')

    log.info("Preparing static search path for %s", theme)
    themes_inheritance_chain = []
    themes_paths = [pkg_resources.resource_filename('aybu.website', 'templates')]
    while theme:
        themes_inheritance_chain.insert(0, theme)
        if theme.parent_name:
            theme = db.themes.filter(db.themes.name == theme.parent_name).one()
        else:
            theme = None

    for theme in themes_inheritance_chain:
        log.info('-- Adding %s' % (theme.name))

        theme_static_spec = 'aybu.themes.%s:/public/' % theme.name
        log.info("Adding '%s' as override for static files", theme_static_spec)
        config.override_asset(
            to_override = 'aybu.website:static/',
            override_with = theme_static_spec
        )

        """
        favicon = '%sfavicon.ico' % (theme_static_spec)
        log.info("Adding '%s' as override for favicon", favicon)
        config.override_asset(
            to_override = 'aybu.website:static/favicon.ico',
            override_with = favicon
        )
        """

        theme_templates_spec = 'aybu.themes.%s:/templates/' % theme.name
        log.info("Adding '%s' as override for templates", theme_templates_spec)
        config.override_asset(
            to_override='aybu.website:templates/',
            override_with=theme_templates_spec
        )
        theme_path = pkg_resources.\
                resource_filename('aybu.themes.%s' % (theme.name),
                                  'templates')

        log.info("Adding '%s' to mako directories", theme_path)
        themes_paths.insert(0, theme_path)

    log.info('-- Adding Instance')
    settings = config.get_settings()
    try:
        instance_name = settings['instance']
        instance_module_name = "aybu.instances.%s" % (instance_name)

        if instance_name is None or instance_name == '':
            raise KeyError()
        else:
            instance_static_spec = '%s:/public/' % instance_module_name
            log.info("Adding '%s' as override for static files",
                     instance_static_spec)
            config.override_asset(
                to_override = 'aybu.website:static/',
                override_with = instance_static_spec
            )

            """
            favicon = '%sfavicon.ico' % (instance_static_spec)
            log.info("Adding '%s' as override for favicon", favicon)
            config.override_asset(
                to_override = 'aybu.website:static/favicon.ico',
                override_with = favicon
            )
            """

            instance_templates_spec = '%s:/templates/' % instance_module_name
            log.info("Adding '%s' as override for templates",
                     instance_templates_spec)
            config.override_asset(
                to_override='aybu.website:templates/',
                override_with=instance_templates_spec
            )

            instance_template_path = pkg_resources.\
                                     resource_filename(instance_module_name,
                                                       'templates/')
            log.info("Adding '%s' to mako directories", instance_template_path)
            themes_paths.insert(0, instance_template_path)


            instance_static_path = pkg_resources.\
                                   resource_filename(instance_module_name,
                                                     'public/')

            upload_path = os.path.join(instance_static_path, 'uploads')

            if os.path.isdir(upload_path):
                if not os.access(upload_path, os.W_OK):
                    log.critical("*" * 79)
                    log.critical("Instance upload dir '%s' is not writable",
                                 upload_path)
                    log.critical('Uploads will NOT work')
                    log.critical("*" * 79)
            else:
                log.critical("*" * 79)
                log.critical("Instance upload dir '%s' does not exists",
                             upload_path)
                log.critical('Uploads will NOT work')
                log.critical("*" * 79)

            # Setup Pufferfish entities
            File.private_path = upload_path
            Image.private_path = upload_path
            File.base_path = os.path.join(upload_path, "files")
            Image.base_path = os.path.join(upload_path, "images")
            try:
                os.mkdir(File.base_path)
            except OSError:
                pass
            try:
                os.mkdir(Image.base_path)
            except OSError:
                pass


    except KeyError as e:
        log.critical("*" * 79)
        log.critical("No instance")
        log.critical('Uploads and instance-specific templates/static will NOT work')
        log.critical("*" * 79)
        raise e

    config.add_settings({
        'mako.directories': themes_paths,
        'mako.strict_undefined': 'true',
    })
