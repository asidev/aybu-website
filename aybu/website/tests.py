#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from pyramid import testing
from logging import getLogger

log = getLogger(__name__)


"""
class ViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from aybu.website.views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['project'], 'aybu-website')
"""
