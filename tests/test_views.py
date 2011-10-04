#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . test_base import BaseTests
from pyramid.httpexceptions import HTTPMovedPermanently


class ViewTests(BaseTests):

    def test_favicon(self):
        from aybu.website.views import favicon
        self.assertRaises(HTTPMovedPermanently, favicon, self.req)

    def test_sitemap(self):
        from aybu.website.views import sitemap
        resp = sitemap(self.ctx, self.req)
        self.assertEqual(resp, {})
        self.assertEqual(self.req.response.content_type, "text/xml")

    def test_show_not_found_error(self):
        from aybu.website.views import show_not_found_error
        self.assertEqual(show_not_found_error(self.ctx, self.req), {})

    def test_choose_default_language(self):
        self.setup_model()
        from aybu.website.views import choose_default_language
        resp = choose_default_language(self.ctx, self.req)



