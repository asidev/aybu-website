#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

"""Setup the aybu application"""

import logging

from pyramid.paster import bootstrap

from sqlalchemy import engine_from_config

from aybu.website.models import Keyword, Theme
#from aybu.website.models import File, Image, Banner
from aybu.website.models import Language
from aybu.website.models import Node, Menu, Page, Section, ExternalLink
from aybu.website.models import InternalLink, NodeInfo
from aybu.website.models import Setting, SettingType
from aybu.website.models import User, Group
from aybu.website.models import View, ViewDescription

from aybu.website.models.base import Base

import ConfigParser
import os
import tempfile
import time
import logging
import shlex
import subprocess
import sys

from paste.script import command


class WebSetupCommand(command.Command):

    min_args = 0
    usage = ""
    summary = """Fill the database"""
    description = """\
    This command fill the website database using configuration ini supplied.
    """

    parser = command.Command.standard_parser(verbose=True)

    """
    parser.add_option("-u", "--dburi",
                      action="store",
                      dest="dburi",
                      default=None,
                      help="URI for database connection")
    """

    def command(self):
        if not "VIRTUAL_ENV" in os.environ:
            raise command.BadCommand("This command MUST be executed "
                                     "inside a virtual env!")

        if self.verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.WARN)
        self.log = logging.getLogger(__name__)

        if not self.args:
            raise command.BadCommand("You must give a config file")

        self.log.debug("Setting up database")

        ini_file = self.args[0]
        if not ini_file.startswith("/"):
            ini_file = os.path.join(os.getcwd(), ini_file)
        config = ConfigParser.ConfigParser()
        config.read(ini_file)

        """
        dburi = config.get("app:aybu-website", "sqlalchemy.url")
        if self.options.dburi:
            dburi = self.options.dburi
        print dburi
        """

        print config

        """
        engine = engine_from_config(config, 'sqlalchemy.')
        Base.metadata.create_all(engine)
        """

        """
        # Create the tables if they don't already exist
        metadata.drop_all()
        metadata.create_all()

        languages = [
            #(id, lang, country, enabled)
            {'id': 1, 'lang': u'it', 'country': u'IT', 'enabled': True},
            {'id': 2, 'lang': u'en', 'country': u'GB', 'enabled': True},
            {'id': 3, 'lang': u'es', 'country': u'ES', 'enabled': True},
            {'id': 4, 'lang': u'de', 'country': u'DE', 'enabled': False},
            {'id': 5, 'lang': u'fr', 'country': u'FR', 'enabled': False},
            {'id': 6, 'lang': u'ru', 'country': u'RU', 'enabled': False},
            {'id': 7, 'lang': u'zh', 'country': u'CN', 'enabled': False}
        ]
        Language.table.insert().execute(languages)

        setting_types = [
            #(name)
            {'name': u'txt'},
            {'name': u'html'},
            {'name': u'image'},
            {'name': u'file'},
            {'name': u'checkbox'}
        ]
        SettingType.table.insert().execute(setting_types)

        settings = [
            #(name, value, raw_type, ui_administrable, type_name)
            {'name': u'site_title', 'value': u'Asidev CMS', 'raw_type': u'unicode', 'ui_administrable': True, 'type_name': u'txt'},
            {'name': u'theme_name', 'value': u'moma', 'raw_type': u'unicode', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'footer_info', 'value': u'<strong>Asidev s.r.l.</strong> © 2008', 'raw_type': u'unicode', 'ui_administrable': True, 'type_name': u'html'},
            {'name': u'reseller_name', 'value': u'VB Site', 'raw_type': u'unicode', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'reseller_link', 'value': u'http://www.vbsite.it', 'raw_type': u'unicode', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'template_levels', 'value': u'3', 'raw_type': u'int', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'main_menu_levels', 'value': u'2', 'raw_type': u'int', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'max_menus', 'value': u'1', 'raw_type': u'int', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'max_languages', 'value': u'3', 'raw_type': u'int', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'image_full_size', 'value': u'600', 'raw_type': u'int', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'max_pages', 'value': u'10', 'raw_type': u'int', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'contact_dst_email_1', 'value': u'l.frosini@asidev.com', 'raw_type': u'unicode', 'ui_administrable': True, 'type_name': u'txt'},
            {'name': u'banner', 'value': u'banner.png', 'raw_type': u'unicode', 'ui_administrable': False, 'type_name': u'image'},
            {'name': u'banner_width', 'value': u'940', 'raw_type': u'int', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'banner_height', 'value': u'320', 'raw_type': u'int', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'logo', 'value': u'logo.png', 'raw_type': u'unicode', 'ui_administrable': False, 'type_name': u'image'},
            {'name': u'logo_width', 'value': u'340', 'raw_type': u'int', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'logo_height', 'value': u'120', 'raw_type': u'int', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'debug', 'value': u'True', 'raw_type': u'bool', 'ui_administrable': False, 'type_name': u'checkbox'},
            {'name': u'max_files', 'value': u'10', 'raw_type': u'int', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'max_images', 'value': u'20', 'raw_type': u'int', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'proxy_enabled', 'value': u'False', 'raw_type': u'bool', 'ui_administrable': False, 'type_name': u'checkbox'},
            {'name': u'proxy_address', 'value': u'127.0.0.1', 'raw_type': u'str', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'proxy_port', 'value': u'80', 'raw_type': u'int', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'proxy_purge_timeout', 'value': u'2', 'raw_type': u'int', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'page_expire_sec', 'value': u'300', 'raw_type': u'int', 'ui_administrable': False, 'type_name': u'txt'},
            {'name': u'head_info', 'value': u'', 'raw_type': u'unicode', 'ui_administrable': True, 'type_name': u'txt'},
            {'name': u'google_analytics_code', 'value': u'', 'raw_type': u'unicode', 'ui_administrable': True, 'type_name': u'txt'},
            {'name': u'addthis', 'value': u'', 'raw_type': u'unicode', 'ui_administrable': True, 'type_name': u'txt'},
            {'name': u'addthis_url', 'value': u'', 'raw_type': u'unicode', 'ui_administrable': True, 'type_name': u'txt'},
            {'name': u'disqus', 'value': u'', 'raw_type': u'unicode', 'ui_administrable': True, 'type_name': u'txt'},
            {'name': u'facebook', 'value': u'', 'raw_type': u'unicode', 'ui_administrable': True, 'type_name': u'txt'},
            {'name': u'twitter', 'value': u'', 'raw_type': u'unicode', 'ui_administrable': True, 'type_name': u'txt'}
        ]
        Setting.table.insert().execute(settings)

        asidev = User(id=1, username=u'info@asidev.com', password=str('cambiami'))

        g = Group(name=u'admin')
        g.users.append(asidev)

        views = [
            {'id': 1, 'name': u'GENERIC', 'fs_view_path': '/pages/generic_content.mako'},
            {'id': 2, 'name': u'CONTACTS', 'fs_view_path': '/pages/contacts.mako'}
        ]
        View.table.insert().execute(views)

        views_descriptions = [
            {'id': 1, 'description': u'Pagina di contenuto generico', 'view_id': 1, 'lang_id': 1},
            {'id': 2, 'description': u'Generic content page', 'view_id': 1, 'lang_id': 2},
            {'id': 3, 'description': u'Pagina con form di contatto', 'view_id': 2, 'lang_id': 1},
            {'id': 4, 'description': u'Contact form page', 'view_id': 2, 'lang_id': 2}
        ]
        ViewDescription.table.insert().execute(views_descriptions)

        nodes = [
            # (id, parent_id, weight, row_type)
            {'id': 1, 'parent_id': None, 'weight': 1, 'row_type': 'menu', 'view_id': None, 'url': None, 'linked_to_id': None},  # Menu Principale
            {'id': 2, 'parent_id': 1, 'weight': 1, 'row_type': 'page', 'view_id': 1, 'url': None, 'linked_to_id': None},  # Home
            {'id': 3, 'parent_id': 1, 'weight': 3, 'row_type': 'page', 'view_id': 2, 'url': None, 'linked_to_id': None},  # Contatti
            {'id': 4, 'parent_id': 1, 'weight': 2, 'row_type': 'section', 'view_id': None, 'url': None, 'linked_to_id': None},   # Azienda
            {'id': 5, 'parent_id': 4, 'weight': 1, 'row_type': 'page', 'view_id': 1, 'url': None, 'linked_to_id': None},  # Chi Siamo
            {'id': 6, 'parent_id': 4, 'weight': 2, 'row_type': 'page', 'view_id': 1, 'url': None, 'linked_to_id': None},  # La nostra Storia
            {'id': 7, 'parent_id': 1, 'weight': 4, 'row_type': 'internallink', 'view_id': None, 'url': None, 'linked_to_id': 3},  # Link -> Contatti
            {'id': 8, 'parent_id': 1, 'weight': 5, 'row_type': 'externallink', 'view_id': None, 'url': 'http://www.asidev.com', 'linked_to_id': None},  # ExtLink
            {'id': 9, 'parent_id': 1, 'weight': 6, 'row_type': 'page', 'view_id': 1, 'url': None, 'linked_to_id': None},  # Soluzioni
            {'id': 10, 'parent_id': 9, 'weight': 1, 'row_type': 'page', 'view_id': 1, 'url': None, 'linked_to_id': None},  # PEC
            {'id': 11, 'parent_id': None, 'weight': 2, 'row_type': 'menu', 'view_id': None, 'url': None, 'linked_to_id': None}  # Pagine Orfane
        ]
        Node.table.insert().execute(nodes)

        pages = [
            {'label': u'Home', 'title': u'Pagina Principale', 'url_part': u'index', 'content': u'<h2>Pagina Principale</h2>', 'lang_id': 1, 'node_id': 2},
            {'label': u'Home', 'title': u'Home Page', 'url_part': u'index', 'content': u'<h2>Home Page</h2>', 'lang_id': 2, 'node_id': 2},
            {'label': u'Home', 'title': u'Primera Pagina', 'url_part': u'index', 'content': u'<h2>Primera Pagina</h2>', 'lang_id': 3, 'node_id': 2},
            {'label': u'Contatti', 'title': u'Contatti', 'url_part': u'contatti', 'content': u'<h2>Contatti</h2>', 'lang_id': 1, 'node_id': 3},
            {'label': u'Contacts', 'title': u'Contacts', 'url_part': u'contacts', 'content': u'<h2>Contacts</h2>', 'lang_id': 2, 'node_id': 3},
            {'label': u'Contacto', 'title': u'Contacto', 'url_part': u'contacto', 'content': u'<h2>Contacto</h2>', 'lang_id': 3, 'node_id': 3},
            {'label': u'Azienda', 'title': u'Azienda', 'url_part': u'azienda', 'content':None, 'lang_id': 1, 'node_id': 4},
            {'label': u'Company', 'title': u'Company', 'url_part': u'company', 'content':None, 'lang_id': 2, 'node_id': 4},
            {'label': u'Empresa', 'title': u'Empresa', 'url_part': u'empresa', 'content':None, 'lang_id': 3, 'node_id': 4},
            {'label': u'Chi Siamo', 'title': u'Chi Siamo', 'url_part': u'chi_siamo', 'content': u'<h2>Chi Siamo</h2>', 'lang_id': 1, 'node_id': 5},
            {'label': u'About Us', 'title': u'About Us', 'url_part': u'about_us', 'content': u'<h2>About Us</h2>', 'lang_id': 2, 'node_id': 5},
            {'label': u'Quiénes somos', 'title': u'Quiénes somos', 'url_part': u'quienes_somos', 'content': u'<h2>Quiénes somos</h2>', 'lang_id': 3, 'node_id': 5},
            {'label': u'La nostra storia', 'title': u'La nostra storia', 'url_part': u'la_nostra_storia', 'content': u'<h2>La nostra storia</h2>', 'lang_id': 1, 'node_id': 6},
            {'label': u'Our History', 'title': u'Our History', 'url_part': u'our_history', 'content': u'<h2>Our History</h2>', 'lang_id': 2, 'node_id': 6},
            {'label': u'Nuestra Historia', 'title': u'Nuestra Historia', 'url_part': u'nuestra_historia', 'content': u'<h2>Nuestra Historia</h2>', 'lang_id': 3, 'node_id': 6},
            {'label': u'Collegamento Interno', 'title': None, 'url_part': None, 'content':None, 'lang_id': 1, 'node_id': 7},
            {'label': u'Internal Link', 'title': None, 'url_part': None, 'content':None, 'lang_id': 2, 'node_id': 7},
            {'label': u'Conexión Interna', 'title': None, 'url_part': None, 'content':None, 'lang_id': 3, 'node_id': 7},
            {'label': u'Sviluppatore', 'title': None, 'url_part': None, 'content':None, 'lang_id': 1, 'node_id': 8},
            {'label': u'Developer', 'title': None, 'url_part': None, 'content':None, 'lang_id': 2, 'node_id': 8},
            {'label': u'Desarrollador', 'title': None, 'url_part': None, 'content':None, 'lang_id': 3, 'node_id': 8},
            {'label': u'Soluzioni', 'title': u'Soluzioni', 'url_part': u'soluzioni', 'content': u'<h2>Soluzioni</h2>', 'lang_id': 1, 'node_id': 9},
            {'label': u'Solutions', 'title': u'Solutions', 'url_part': u'solutions', 'content': u'<h2>Solutions</h2>', 'lang_id': 2, 'node_id': 9},
            {'label': u'Solución', 'title': u'Solución', 'url_part': u'solucion', 'content': u'<h2>Solución</h2>', 'lang_id': 3, 'node_id': 9},
            {'label': u'PEC', 'title': u'PEC', 'url_part': u'pec', 'content': u'<h2>P.E.C.</h2>', 'lang_id': 1, 'node_id': 10},
            {'label': u'ECM', 'title': u'ECM', 'url_part': u'ecm', 'content': u'<h2>Electronic Certified Mail</h2>', 'lang_id': 2, 'node_id': 10},
            {'label': u'CEC', 'title': u'CEC', 'url_part': u'cec', 'content': u'<h2>Correo Electronico Certifigado</h2>', 'lang_id': 3, 'node_id': 10},
        ]
        NodeInfo.table.insert().execute(pages)

        themes = [
            #(name, parent_name)
            {'name': u'base', 'parent_name': None},
            {'name': u'uffizi', 'parent_name': 'base'},
            {'name': u'moma', 'parent_name': u'uffizi'},
        ]
        Theme.table.insert().execute(themes)

        dbsession.commit()

        query = "UPDATE users SET password='8593d55f4d3044f9a1a84f75a81bb9945a10c095' WHERE username='info@asidev.com';"
        metadata.bind.execute(query)
        """
