#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.website.request import Request
from aybu.website.models.base import Base
from aybu.website.models.file import File
from aybu.website.models.file import Image
from aybu.website.resources import get_root_resource
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy import engine_from_config
from sqlalchemy.ext.sqlsoup import SqlSoup
from sqlalchemy.orm.exc import NoResultFound
import logging
import os
import pkg_resources

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
    #config.add_route('static', '/static')
    # Put URL dispatch configuration statements before Traversal ones!!!
    config.add_route('root', '/*traverse', factory=get_root_resource)


def add_views(config):

    # Views called after URL dispatch.

    config.add_view(route_name='favicon',
                    view='aybu.website.views.favicon')

    config.add_view(route_name='robots',
                    view='aybu.website.views.robots')

    config.add_view(route_name='sitemap',
                    renderer='/sitemap.mako',
                    view='aybu.website.views.sitemap')

    # Views called after Traversal.

    config.add_view(route_name='root',
                    context='aybu.website.resources.NoLanguage',
                    view='aybu.website.views.choose_default_language')

    config.add_view(route_name='root',
                    context='aybu.website.models.Language',
                    view='aybu.website.views.redirect_to_homepage')

    config.add_view(route_name='root',
                    context='aybu.website.models.NodeInfo',
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
    config.add_static_view('static', 'aybu.website:static')

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
        theme_static_spec = 'aybu.themes:%s/public/' % theme.name
        log.info("Adding '%s' as override for static files", theme_static_spec)
        config.override_asset(
            to_override='aybu.website:static/',
            override_with=theme_static_spec
        )
        theme_templates_spec = 'aybu.themes:%s/templates/' % theme.name
        log.info("Adding '%s' as override for templates", theme_templates_spec)
        config.override_asset(
            to_override='aybu.website:templates/',
            override_with=theme_templates_spec
        )
        theme_path = pkg_resources.\
                resource_filename('aybu.themes',
                                  '%s/templates' % (theme.name))

        log.info("Adding '%s' to mako directories", theme_path)
        themes_paths.insert(0, theme_path)

    log.info('Adding instance paths')
    settings = config.get_settings()
    try:
        inst_data = settings['instance_data_dir']
        if not os.path.isdir(inst_data):
            log.critical("*" * 79)
            log.critical("No such instance data directory '%s'", inst_data)
            log.critical('Uploads and instance-specific templates/static '
                         'will NOT work')
            log.critical("*" * 79)

        else:
#           FIXME: per instance static and templates overrides is disabled
#           temporary, as override_asset API needs a setuptool package so
#           we need to figure out how to deploy this.
#           Actually, for templates it can work as we configure mako by
#           itself, so it get it's own search path, but the problem remains
#           for static files (i.e.: favicon)
#           inst_templs = settings.get('instance_templates_dir',
#                                      os.path.join(inst_data, 'templates'))
#           inst_static = settings.get('instance_static_dir',
#                                      os.path.join(inst_data, 'static'))
#
#            # overriding templates with instance-specific ones
#            if os.path.isdir(inst_templs):
#                log.info("Installing override for instance templates @'%s'",
#                         inst_templs)
#                config.override_asset(
#                    to_override='aybu.website:templates/',
#                    override_with=inst_templs)
#                themes_paths.insert(0, inst_templs)
#            else:
#                log.warn("Instance template dir '%s' does not exists",
#                         inst_templs)
#
#            # overriding static files with instance specific
#            if os.path.isdir(inst_static):
#                log.info("Installing override for instance static files @'%s'",
#                         inst_static)
#                config.override_asset(
#                    to_override='aybu.website:static/',
#                    override_with=inst_static)
#            else:
#                log.warn("Instance static dir '%s' does not exists",
#                         inst_static)

            inst_uploads = os.path.join(inst_data, 'static/uploads')
            # Adding upload directory
            if os.path.isdir(inst_uploads):
                if not os.access(inst_uploads, os.W_OK):
                    log.critical("*" * 79)
                    log.critical("Instance upload dir '%s' is not writable",
                                 inst_uploads)
                    log.critical('Uploads will NOT work')
                    log.critical("*" * 79)

                log.info('Adding upload dir')
                config.add_static_view('uploads/', inst_uploads)

            else:
                log.critical("*" * 79)
                log.critical("Instance upload dir '%s' does not exists",
                             inst_uploads)
                log.critical('Uploads will NOT work')
                log.critical("*" * 79)

            # Setup Pufferfish entities
            File.private_path = inst_data
            Image.private_path = inst_data
            File.base_path = os.path.join(inst_uploads, "files")
            Image.base_path = os.path.join(inst_uploads, "images")
            try:
                os.mkdir(File.base_path)
            except OSError:
                pass
            try:
                os.mkdir(Image.base_path)
            except OSError:
                pass


    except KeyError as e:
        raise e
        log.error("'%s', cannot configure instance data", e)

    config.add_settings({
        'mako.directories': themes_paths,
        'mako.strict_undefined': 'true',
    })
