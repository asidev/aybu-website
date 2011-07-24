#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.website.models.base import Base
from aybu.website.models.file import Banner
from aybu.website.models.file import File
from aybu.website.models.file import Image
from aybu.website.models.language import Language
from aybu.website.models.node import ExternalLink
from aybu.website.models.node import InternalLink
from aybu.website.models.node import Menu
from aybu.website.models.node import Node
from aybu.website.models.node import NodeInfo
from aybu.website.models.node import Page
from aybu.website.models.node import Section
from aybu.website.models.setting import Setting
from aybu.website.models.setting import SettingType
from aybu.website.models.theme import Keyword
from aybu.website.models.theme import Theme
from aybu.website.models.user import Group
from aybu.website.models.user import User
from aybu.website.models.view import View
from aybu.website.models.view import ViewDescription
from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker


def engine_from_config_parser(config):

    options = {}

    for section in config.sections():
        for option in config.options(section):
            if option.startswith('sqlalchemy.'):
                options[option] = config.get(section, option)

    return engine_from_config(options)


def populate(config):

    engine = engine_from_config_parser(config)
    session = scoped_session(sessionmaker())
    session.configure(bind=engine)

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    languages = {}
    for language in [Language(id=1, lang=u'it', country=u'IT', enabled=True),
                     Language(id=2, lang=u'en', country=u'GB', enabled=True),
                     Language(id=3, lang=u'es', country=u'ES', enabled=True),
                     Language(id=4, lang=u'de', country=u'DE', enabled=False),
                     Language(id=5, lang=u'fr', country=u'FR', enabled=False),
                     Language(id=6, lang=u'ru', country=u'RU', enabled=False),
                     Language(id=7, lang=u'zh', country=u'CN', enabled=False)]:

        session.add(language)
        languages[language.id] = language

    setting_types = {}
    for setting_type in [SettingType(name=u'txt'),
                         SettingType(name=u'html'),
                         SettingType(name=u'image'),
                         SettingType(name=u'file'),
                         SettingType(name=u'checkbox')]:

        session.add(setting_type)
        setting_types[setting_type.name] = setting_type

    settings = {}
    for setting in [Setting(name=u'site_title', value=u'Asidev CMS',
                            raw_type=u'unicode', ui_administrable=True,
                            type_name=u'txt'),
                    Setting(name=u'theme_name', value=u'moma',
                            raw_type=u'unicode', ui_administrable=False,
                            type_name=u'txt'),
                    Setting(name=u'footer_info',
                            value=u'<strong>Asidev s.r.l.</strong> © 2008',
                            raw_type=u'unicode', ui_administrable=True,
                            type_name=u'html'),
                    Setting(name=u'reseller_name', value=u'VB Site',
                            raw_type=u'unicode', ui_administrable=False,
                            type_name=u'txt'),
                    Setting(name=u'reseller_link',
                            value=u'http://www.vbsite.it', raw_type=u'unicode',
                            ui_administrable=False, type_name=u'txt'),
                    Setting(name=u'template_levels', value=u'3',
                            raw_type=u'int', ui_administrable=False,
                            type_name=u'txt'),
                    Setting(name=u'main_menu_levels', value=u'2', 
                            raw_type=u'int', ui_administrable=False,
                            type_name=u'txt'),
                    Setting(name=u'max_menus', value=u'1', raw_type=u'int',
                            ui_administrable=False, type_name=u'txt'),
                    Setting(name=u'max_languages', value=u'3', raw_type=u'int',
                            ui_administrable=False, type_name=u'txt'),
                    Setting(name=u'image_full_size', value=u'600',
                            raw_type=u'int', ui_administrable=False,
                            type_name=u'txt'),
                    Setting(name=u'max_pages', value=u'10', raw_type=u'int',
                            ui_administrable=False, type_name=u'txt'),
                    Setting(name=u'contact_dst_email_1',
                            value=u'l.frosini@asidev.com', raw_type=u'unicode',
                            ui_administrable=True, type_name=u'txt'),
                    Setting(name=u'banner', value=u'banner.png',
                            raw_type=u'unicode', ui_administrable=False,
                            type_name=u'image'),
                    Setting(name=u'banner_width', value=u'940',
                            raw_type=u'int', ui_administrable=False,
                            type_name=u'txt'),
                    Setting(name=u'banner_height', value=u'320',
                            raw_type=u'int', ui_administrable=False,
                            type_name=u'txt'),
                    Setting(name=u'logo', value=u'logo.png',
                            raw_type=u'unicode', ui_administrable=False,
                            type_name=u'image'),
                    Setting(name=u'logo_width', value=u'340', raw_type=u'int',
                            ui_administrable=False, type_name=u'txt'),
                    Setting(name=u'logo_height', value=u'120', raw_type=u'int',
                            ui_administrable=False, type_name=u'txt'),
                    Setting(name=u'debug', value=u'True', raw_type=u'bool',
                            ui_administrable=False, type_name=u'checkbox'),
                    Setting(name=u'max_files', value=u'10', raw_type=u'int',
                            ui_administrable=False, type_name=u'txt'),
                    Setting(name=u'max_images', value=u'20', raw_type=u'int',
                            ui_administrable=False, type_name=u'txt'),
                    Setting(name=u'proxy_enabled', value=u'False',
                            raw_type=u'bool', ui_administrable=False,
                            type_name=u'checkbox'),
                    Setting(name=u'proxy_address', value=u'127.0.0.1',
                            raw_type=u'str', ui_administrable=False,
                            type_name=u'txt'),
                    Setting(name=u'proxy_port', value=u'80', raw_type=u'int',
                            ui_administrable=False, type_name=u'txt'),
                    Setting(name=u'proxy_purge_timeout', value=u'2',
                            raw_type=u'int', ui_administrable=False, 
                            type_name=u'txt'),
                    Setting(name=u'page_expire_sec', value=u'300',
                            raw_type=u'int', ui_administrable=False,
                            type_name=u'txt'),
                    Setting(name=u'head_info', value=u'', raw_type=u'unicode',
                            ui_administrable=True, type_name=u'txt'),
                    Setting(name=u'google_analytics_code', value=u'',
                            raw_type=u'unicode', ui_administrable=True,
                            type_name=u'txt'),
                    Setting(name=u'addthis', value=u'', raw_type=u'unicode',
                            ui_administrable=True, type_name=u'txt'),
                    Setting(name=u'addthis_url', value=u'', raw_type=u'unicode',
                            ui_administrable=True, type_name=u'txt'),
                    Setting(name=u'disqus', value=u'', raw_type=u'unicode',
                            ui_administrable=True, type_name=u'txt'),
                    Setting(name=u'facebook', value=u'', raw_type=u'unicode',
                            ui_administrable=True, type_name=u'txt'),
                    Setting(name=u'twitter', value=u'', raw_type=u'unicode',
                            ui_administrable=True, type_name=u'txt')]:

        session.add(setting)
        settings[setting.name] = setting

    user = User(username=u'info@asidev.com', password=str('cambiami'))
    session.add(user)
    users = {user.username: user}

    group = Group(name=u'admin')
    group.users.append(user)
    session.add(group)
    groups = {group.name: group}


    views = {}
    for view in [View(id=1, name=u'GENERIC', 
                      fs_view_path='/pages/generic_content.mako'),
                 View(id=2, name=u'CONTACTS', 
                      fs_view_path='/pages/contacts.mako')]:

        session.add(view)
        views[view.id] = view

    views_descriptions = {}
    for item in [ViewDescription(id=1,
                                 description=u'Pagina di contenuto generico',
                                 view=views[1], language=languages[1]),
                 ViewDescription(id=2, description=u'Generic content page',
                                 view=views[1], language=languages[2]),
                 ViewDescription(id=3,
                                 description=u'Pagina con form di contatto',
                                 view=views[2], language=languages[1]),
                 ViewDescription(id=4, description=u'Contact form page',
                                 view=views[2], language=languages[2])]:

        session.add(item)
        views_descriptions[item.id] = item

    menus = {}
    for menu in [Menu(id=1, parent=None, weight=1),
                 Menu(id=11, parent=None, weight=2)]:

        session.add(menu)
        menus[menu.id] = menu

    pages = {}
    for page in [Page(id=2, parent=menus[1], weight=1, view=views[1]),
                 Page(id=3, parent=menus[1], weight=3, view=views[2]),
                 Page(id=9, parent=menus[1], weight=6, view=views[1])]:

        session.add(page)
        pages[page.id] = page

    section = Section(id=4, parent=menus[1], weight=2)
    session.add(section)
    sections = {4: section}

    for page in [Page(id=5, parent=sections[4], weight=1, view=views[1]),
                 Page(id=6, parent=sections[4], weight=2, view=views[1])]:

        session.add(page)
        pages[page.id] = page

    internal_link = InternalLink(id=7,
                                 parent=menus[1], weight=4, linked_to=pages[3])
    session.add(internal_link)
    internal_links = {internal_link.id: internal_link}

    page = Page(id=10, parent=pages[9], weight=1, view=views[1])
    session.add(page)
    pages[page.id] = page

    external_link = ExternalLink(id=8, parent=menus[1], weight=5, 
                                 url=u'http://www.asidev.com')
    session.add(external_link)
    external_links = {external_link.id: external_link}

    nodes_info = {}
    for info in [NodeInfo(id=1, label=u'Home', title=u'Pagina Principale', 
                          url_part=u'index',
                          content=u'<h2>Pagina Principale</h2>',
                          lang=languages[1], node=pages[2]),
                 NodeInfo(id=2, label=u'Home', title=u'Home Page',
                          url_part=u'index', content=u'<h2>Home Page</h2>', 
                          lang=languages[2], node=pages[2]),
                 NodeInfo(id=3, label=u'Home', title=u'Primera Pagina',
                          url_part=u'index', content=u'<h2>Primera Pagina</h2>',
                          lang=languages[3], node=pages[2]),
                 NodeInfo(id=4, label=u'Contatti', title=u'Contatti',
                          url_part=u'contatti', content=u'<h2>Contatti</h2>',
                          lang=languages[1], node=pages[3]),
                 NodeInfo(id=5, label=u'Contacts', title=u'Contacts',
                          url_part=u'contacts', content=u'<h2>Contacts</h2>',
                          lang=languages[2], node=pages[3]),
                 NodeInfo(id=6, label=u'Contacto', title=u'Contacto',
                          url_part=u'contacto', content=u'<h2>Contacto</h2>',
                          lang=languages[3], node=pages[3]),
                 NodeInfo(id=7, label=u'Azienda', title=u'Azienda',
                          url_part=u'azienda', lang=languages[1],
                          node=sections[4]),
                 NodeInfo(id=8, label=u'Company', title=u'Company',
                          url_part=u'company', lang=languages[2],
                          node=sections[4]),
                 NodeInfo(id=9, label=u'Empresa', title=u'Empresa',
                          url_part=u'empresa', lang=languages[3],
                          node=sections[4]),
                 NodeInfo(id=10, label=u'Chi Siamo', title=u'Chi Siamo',
                          url_part=u'chi_siamo', content=u'<h2>Chi Siamo</h2>',
                          lang=languages[1], node=pages[5]),
                 NodeInfo(id=11, label=u'About Us', title=u'About Us',
                          url_part=u'about_us', content=u'<h2>About Us</h2>',
                          lang=languages[2], node=pages[5]),
                 NodeInfo(id=12, label=u'Quiénes somos', title=u'Quiénes somos',
                          url_part=u'quienes_somos',
                          content=u'<h2>Quiénes somos</h2>',
                          lang=languages[3], node=pages[5]),
                 NodeInfo(id=13, label=u'La nostra storia', 
                          title=u'La nostra storia',
                          url_part=u'la_nostra_storia',
                          content=u'<h2>La nostra storia</h2>',
                          lang=languages[1], node=pages[6]),
                 NodeInfo(id=14, label=u'Our History', title=u'Our History',
                          url_part=u'our_history',
                          content=u'<h2>Our History</h2>',
                          lang=languages[2], node=pages[6]),
                 NodeInfo(id=15, label=u'Nuestra Historia',
                          title=u'Nuestra Historia',
                          url_part=u'nuestra_historia',
                          content=u'<h2>Nuestra Historia</h2>', 
                          lang=languages[3], node=pages[6]),
                 NodeInfo(id=16, label=u'Collegamento Interno', 
                          lang=languages[1], node=internal_links[7]),
                 NodeInfo(id=17, label=u'Internal Link',lang=languages[2],
                          node=internal_links[7]),
                 NodeInfo(id=18, label=u'Conexión Interna', lang=languages[3],
                          node=internal_links[7]),
                 NodeInfo(id=19, label=u'Sviluppatore', lang=languages[1],
                          node=external_links[8]),
                 NodeInfo(id=20, label=u'Developer', lang=languages[2],
                          node=external_links[8]),
                 NodeInfo(id=21, label=u'Desarrollador', lang=languages[3],
                          node=external_links[8]),
                 NodeInfo(id=22, label=u'Soluzioni', title=u'Soluzioni',
                          url_part=u'soluzioni', content=u'<h2>Soluzioni</h2>',
                          lang=languages[1], node=pages[9]),
                 NodeInfo(id=23, label=u'Solutions', title=u'Solutions',
                          url_part=u'solutions', content=u'<h2>Solutions</h2>',
                          lang=languages[2], node=pages[9]),
                 NodeInfo(id=24, label=u'Solución', title=u'Solución',
                          url_part=u'solucion', content=u'<h2>Solución</h2>',
                          lang=languages[3], node=pages[9]),
                 NodeInfo(id=25, label=u'PEC', title=u'PEC', url_part=u'pec',
                          content=u'<h2>P.E.C.</h2>', lang=languages[1],
                          node=pages[10]),
                 NodeInfo(id=26, label=u'ECM', title=u'ECM', url_part=u'ecm',
                          content=u'<h2>Electronic Certified Mail</h2>',
                          lang=languages[2], node=pages[10]),
                 NodeInfo(id=27, label=u'CEC', title=u'CEC', url_part=u'cec',
                          content=u'<h2>Correo Electronico Certifigado</h2>',
                          lang=languages[3], node=pages[10])]:

        session.add(info)
        nodes_info[info.id] = info

    themes = {}
    for theme in [Theme(name=u'base', parent=None),
                  Theme(name=u'uffizi', parent=None),
                  Theme(name=u'moma', parent=None)]:

        session.add(theme)
        themes[theme.name] = theme

    themes['uffizi'].parent = themes['base']
    themes['moma'].parent = themes['uffizi']

    session.flush()

    # Build the NodeInfo.url for each NodeInfo object.
    for info in nodes_info.itervalues():

        if info.url_part is None:
            continue

        url_parts = [info.url_part]

        node = info.node
        while not node.parent is None:
            node = node.parent
            for node_info in node.translations:
                if node_info.lang == info.lang:
                    url_parts.append(node_info.url_part)
                    break

        url_parts.append(info.lang.lang)
        url_parts.reverse()
        info.url = '/' + '/'.join(url_parts) + '.html'

    session.commit()
