#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

import logging
import re

from aybu.core.models import Setting, Language
from recaptcha.client.captcha import submit
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

log = logging.getLogger(__name__)
email_re = re.compile("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?")
name_re = re.compile("[(0-9@*(\)[\]+.,/?:;\"`~\\#$%^&<>)+]")
phone_re = re.compile("^(\+){0,1}([0-9-()]|( ))+$")


def validate_name(field, value):
    error = {}
    success = True
    if name_re.search(value) is None:
        if len(value) < 2:
            error[field] = u"Inserisci almeno 2 caratteri."
            success = False
    else:
        error[field] = u"Numeri o caratteri speciali non sono ammessi."
        success = False

    return dict(success=success, error=error)


def validate_captcha(response, challenge, remote_addr):
    # FIXME: this is nonsense
    private_key = '6LeNHcYSAAAAAM7o91qbVfLAFjxoj336p3LL7YZB'
    result = dict(error={}, success=True)

    try:
        recaptcha_response = submit(challenge, response,  private_key, remote_addr)

        if not recaptcha_response.is_valid:
            result['error']['captcha'] = u"Il testo da lei inserito non " +\
                                           u"corrisponde con quello " +\
                                           u"visualizzato nell'immagine. " +\
                                           u"La preghiamo di riprovare."
            result['success'] = False

    except Exception:
        log.exception('Error validating captcha code')
        result['error']['captcha'] = u"Errore durante la validazione del captcha"
        result['success'] = False

    finally:
        return result


def handle_contact_form(request):
    log.debug("Building contacts form")
    result = dict(
        vars={},
        error={},
        success=True,
        message=u"Grazie per averci contattato. Le risponderemo al più presto."
    )
    form_keys = ('name', 'surname', 'email', 'phone', 'agreement', 'message',
            'captcha')
    for key in form_keys:
        value = request.params.get(key, '')
        result['error'][key] = value.title() \
                               if key in ('name', 'surname') else value

    if len(request.params):
        recipients = request.db_session.query(Setting)\
                 .filter(Setting.name.like(u'contact_dst_email_%')).all()

        if len(recipients) > 0:
            log.debug("Recipients: %s", recipients)
            log.debug("Form has been submitted, validating fields")
            result.update(validate_name('name', request.params.get('name')))
            result.update(validate_name('surname', request.params.get('surname')))
            response_field = request.params.get('recaptcha_response_field', '')
            challenge_field = request.params.get('recaptcha_challenge_field', '')
            result.update(validate_captcha(response_field, challenge_field,
                          request.remote_addr))

            if not email_re.match(request.params.get('email','')):
                result['error']['email'] = u"Inserisci un indirizzo email valido."
                result['success'] = False

            if not phone_re.match(request.params.get('phone', '')):
                result['error']['phone'] = u"Inserisci un numero di telefono valido."
                result['success'] = False

            if len(request.params.get('message', '')) < 10:
                result['error']['message'] = u"Inserisci almeno 10 caratteri."
                result['success'] = False

            if not request.params.get('agreement', '') == 'on':
                result['error']['agreement'] = u"Devi accettare i termini di Privacy"
                result['success'] = False

            # FIXME: use a template!
            body = u"Nome : %s \n" % (request.params.get('name'))
            body = u"%sCognome : %s \n" % (body, request.params.get('surname'))
            body = u"%sTelefono : %s \n\n" % (body, request.params.get('phone'))

            for key, value in request.params.iteritems():
                if key not in form_keys and not key.startswith("recaptcha"):
                    p = key.decode('utf8')
                    body = u"%s%s : %s \n" % (body, p.title(), value)
                    result['vars'][key] = value

            body = u"%sMessaggio : \n%s\n" % (body, request.params.get('message'))

            mailer = get_mailer(request)
            message = Message(subject=u"Nuovo messaggio dal form di contatto web",
                            sender=request.params.get('email'),
                            body=body,
                            recipients=[r.value for r in recipients[0:1]],
                            cc=[r.value for r in recipients[1:]])

            if result['success']:
                log.debug('Form is valid, sending emails')
                try:
                    # mailer.send_immediately(message, fail_silently=False)
                    pass

                except:
                    log.exception("Errore nell'invio del messaggio. \n")
                    result['result_message'] = \
                        u"Errore nell'invio del messaggio. " + \
                        u"Si prega di riprovare più tardi."
                    result['success'] = False
            else:
                result['result_message'] = u"Errore nell'invio del form. " +\
                                           u"Ricontrollare i campi e riprovare."

    # get lang to translate messages
    def_lang = request.registry.settings.get('default_locale_name', 'it')
    lang = request.params.get('_lang', def_lang)
    try:
        request.language = Language.get_by_lang(request.db_session, lang)
    except:
        request.language = Language.get_by_lang(request.db_session, def_lang)

    # translate error message
    for err in result['error']:
        result['errors'][err] = request.translate(err)

    log.debug("Result: %s", result)
    return result
