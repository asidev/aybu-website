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
from . test_base import BaseTests
import collections
from pyramid.testing import DummyRequest

import recaptcha.client.captcha
Response = collections.namedtuple('Response', ['is_valid'])
def closure(challenge, response, private_key, remote_addr):
    if not response:
        raise Exception('faked')
    return Response(is_valid=bool(challenge))

recaptcha.client.captcha.submit = closure
import aybu.website.lib.contact_utils as cu


class ContactTest(BaseTests):

    def add_languages_to_db(self):
        it = Language(lang=u'it', country=u'it')
        self.session.add(it)
        en = Language(lang=u'en', country=u'gb')
        self.session.add(en)
        self.session.commit()

    def add_recipient(self, email):
        st = SettingType(name='txt', raw_type='unicode')
        self.session.add(st)
        self.session.add(Setting(
            name='contact_dst_email_1',
            value=email,
            type=st,
            ui_administrable=1))
        self.session.commit()

    def new_req(self, params):
        def dummy_translate(string):
            return string

        req = DummyRequest(params=params, remote_addr='remote',
                           db_session=self.req.db_session)
        req.translate = dummy_translate
        return req

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

    def test_validate_captcha(self):
        res = cu.validate_captcha('bogus', 'bogus', 'bogus')
        self.assertTrue(res['success'])
        self.assertNotIn('captcha', res['error'])

        res = cu.validate_captcha(False, 'bogus', 'bogus')
        self.assertFalse(res['success'])
        self.assertIn('captcha', res['error'])

        res = cu.validate_captcha(True, None, 'bogus')
        self.assertFalse(res['success'])
        self.assertIn('captcha', res['error'])


    def test_handle_contact_form(self):
        def test_submit(params, success=True, error_field=''):
            req = self.new_req(params)
            res = cu.handle_contact_form(req)
            if success:
                self.assertTrue(res['success'])
            else:
                self.assertFalse(res['success'])
                self.assertIn(error_field, res['error'])

        self.add_languages_to_db()

        # test empty
        res = cu.handle_contact_form(self.req)
        form_keys = ('name', 'surname', 'email', 'phone', 'agreement',
                     'message', 'captcha')
        self.assertFalse(res['success'])
        for key in form_keys:
            self.assertIn(key, res['error'])

        # test valid
        valid_phone = '3334445556'
        valid_agreement = 'on'
        valid_message = 'a message longer than 10 chars'
        valid_email = 'valid@example.com'

        params = dict()
        params['name'] = 'Name'
        params['surname'] = 'Surname'
        params['phone'] = valid_phone
        params['email'] = valid_email
        params['agreement'] = valid_agreement
        params['message'] = valid_message
        params['recaptcha_response_field'] = 'bogus'
        params['recaptcha_challenge_field'] = 'bogus'
        test_submit(params)

        # test email
        for email in ('add', '@dom', 'add@adom', 'aad@dom.', '.@dom.it',
                       'add@dom..it'):
#            print "Testing email %s" % email
            params['email'] = email
            test_submit(params, False, 'email')
        params['email'] = valid_email

        # test phone
        for phone in ('+393334445', '+(39)3334445', '333444555'):
#            print "Testing phone %s" % phone
            params['phone'] = phone
            test_submit(params)

#        for phone in ('3', 'asklaksl', '-333444555',):
#            print "Testing phone %s" % phone
#            params['phone'] = phone
#            test_submit(params, False, 'phone')




        self.add_recipient('test@example.com')
