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

from . test_base import BaseTests
from aybu.core.models import Language
from aybu.core.models import Page
from aybu.core.models import Menu
from aybu.core.models import PageInfo
from aybu.core.models import View

from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.httpexceptions import HTTPTemporaryRedirect


class ViewTests(BaseTests):

    def add_test_data_to_db(self):
        """ Add some pages and languages to the database """
        menu = Menu(id=1, parent=None, weight=1)
        self.session.add(menu)
        npage = Page(id=2, parent=menu, weight=2)
        hpage = Page(id=3, parent=menu, weight=1, home=True)
        dummy_view = View(name='dummy',
                          fs_view_path='test_templates/page.mako')
        hpage.view = dummy_view
        npage.view = dummy_view
        self.session.add(hpage)
        self.session.add(npage)
        it = Language(lang=u'it', country=u'it')
        self.session.add(it)
        en = Language(lang=u'en', country=u'gb')
        self.session.add(en)


        npage_info_it = PageInfo(id=1, label='Normal', title='Normal Page',
                               url_part='normal', url='/en/normal.html',
                               node=npage, lang=en)
        npage_info_en = PageInfo(id=2, label='Normale', title='Pagina Normale',
                               url_part='normale', url='/it/normale.html',
                               node=npage, lang=it)

        self.session.add(npage_info_it)
        self.session.add(npage_info_en)

        hpage_info_it = PageInfo(id=3, label='Home', title='Pagina Principale',
                             url_part='index', url='/it/index.html', node=hpage,
                             lang=it)

        hpage_info_en = PageInfo(id=4, label='Home', title='Main Page',
                             url_part='index', url='/en/index.html', node=hpage,
                             lang=en)

        self.session.add(hpage_info_it)
        self.session.add(hpage_info_en)
        self.session.commit()

    def test_favicon(self):
        from aybu.website.views import favicon
        self.assertRaises(HTTPMovedPermanently, favicon, self.req)

    def test_sitemap(self):
        from aybu.website.views import sitemap
        resp = sitemap(self.ctx, self.req)
        self.assertEqual(resp, {})
        self.assertEqual(self.req.response.content_type, "text/xml")

    def test_robots(self):
        from aybu.website.views import robots
        resp = robots(self.ctx, self.req)
        self.assertEqual(resp, {})
        self.assertEqual(self.req.response.content_type, "text/plain")

    def test_show_not_found_error(self):
        from aybu.website.views import show_not_found_error
        self.assertEqual(show_not_found_error(self.ctx, self.req), {})

    def test_choose_default_language(self):
        from aybu.website.views import choose_default_language
        l = Language(lang='it', country='IT', enabled=True)
        self.session.add(l)
        self.session.commit()
        with self.assertRaises(HTTPTemporaryRedirect) as cm:
            choose_default_language(self.ctx, self.req)
        self.assertEqual(cm.exception.location, "/it")
        self.session.commit()

    def test_negotiate_language(self):
        from aybu.website.views import choose_default_language
        l_it = Language(lang='it', country='IT', enabled=True)
        l_en = Language(lang='en', country='US', enabled=True)
        self.session.add(l_it)
        self.session.add(l_en)
        self.session.commit()
        self.req.accept_language = "en-US,en"
        with self.assertRaises(HTTPTemporaryRedirect) as cm:
            choose_default_language(self.ctx, self.req)
        self.assertEqual(cm.exception.location, "/en")
        self.session.commit()

    def test_redirect_to_homepage(self):
        from aybu.website.views import redirect_to_homepage
        self.add_test_data_to_db()
        hpage_it = PageInfo.get(self.session, 3)
        hpage_en = PageInfo.get(self.session, 4)


        with self.assertRaises(HTTPMovedPermanently) as cm:
            redirect_to_homepage(self.ctx, self.req)

        self.assertEqual(cm.exception.location, hpage_it.url)

        self.req.accept_language = "en-US,en"
        with self.assertRaises(HTTPMovedPermanently) as cm:
            redirect_to_homepage(self.ctx, self.req)
        self.assertEqual(cm.exception.location, hpage_en.url)

        self.session.commit()


    def test_show_page(self):
        from aybu.website.views import show_page
        self.add_test_data_to_db()
        self.ctx = PageInfo.get(self.session, 3)
        dummy_rendererer = self.config.testing_add_renderer(
                                        self.ctx.node.view.fs_view_path)
        show_page(self.ctx, self.req)
        dummy_rendererer.assert_(page=self.ctx, request=self.req)
