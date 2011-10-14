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

from aybu.core.models import Language, Setting, SettingType
import aybu.website.lib.contact_utils as cu
from . test_base import BaseTests


class ContactTest(BaseTests):

    def add_test_data_to_db(self):
        it = Language(lang=u'it', country=u'it')
        self.session.add(it)
        en = Language(lang=u'en', country=u'gb')
        self.session.add(en)
        st = SettingType(name='txt')
        self.session.add(st)
        self.session.add(Setting(
            name='contact_dst_email_1',
            value='test@example.com',
            raw_type='unicode',
            type=st,
            ui_administrable=1))
        self.session.commit()

    def test_validate_name(self):
        def test_string(value, success=False):
            res = cu.validate_name('testfield', value)
            self.assertEqual(res['success'], success)
            if not success:
                self.assertIn('testfield', res['error'])
            else:
                self.assertNotIn('testfield', res['error'])

        test_string("")
        test_string("a")
        test_string('Name', True)
        test_string('My Name', True)
        test_string('My Long Name', True)
        for c in '@*()[]+.,/?:;"`~\#$%^&<>':
            test_string('test' + c)
