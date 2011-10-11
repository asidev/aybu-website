#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

import logging
import re

from aybu.core.models import Setting
from recaptcha.client.captcha import submit
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

log = logging.getLogger(__name__)
email_re = re.compile("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?")
name_re = re.compile("[(0-9@*(\)[\]+.,/?:;\"`~\\#$%^&<>)+]")
phone_re = re.compile("^(\+){0,1}([0-9-()]|( ))+$")


def validate_name(request, value, field):
    ctx = request.tmpl_context
    _ = request.translate
    if name_re.search(value) is None:
        if len(value) < 2:
            ctx.error[field] = _(u"Inserisci almeno 2 caratteri.")
            ctx.success = False
    else:
        ctx.error[field] = _(u"Numeri o caratteri speciali non sono ammessi.")
        ctx.success = False


def validate_captcha(request):
    # FIXME: this is nonsense
    private_key = '6LeNHcYSAAAAAM7o91qbVfLAFjxoj336p3LL7YZB'
    _ = request.translate
    ctx = request.tmpl_context

    try:
        response_field = request.params.get('recaptcha_response_field', '')
        challenge_field = request.params.get('recaptcha_challenge_field', '')
        recaptcha_response = submit(challenge_field, response_field,
                                    private_key, request.remote_addr)

        if not recaptcha_response.is_valid:
            ctx.error['captcha'] = _(u"Il testo da lei inserito non corrisponde con quello visualizzato nell'immagine. La preghiamo di riprovare.")
            ctx.success = False

    except Exception:
        log.exception('Error validating captcha code')
        ctx.error['captcha'] = _(u"Errore durante la validazione del captcha")
        ctx.success = False


def handle_contact_form(request):
    log.debug("Building contacts form")
    ctx = request.tmpl_context
    _ = request.translate
    ctx.vars = {}
    ctx.error = {}
    form_keys = ('name', 'surname', 'email', 'phone', 'agreement', 'message',
            'captcha')
    for key in form_keys:
        ctx.error[key] = ''
        value = request.params.get(key, '')
        setattr(ctx, key, value.title() if key in ('name', 'surname') else value)

    ctx.result_message = "PROVA"
    ctx.success = True

    # FIXME: why old "submit" value is not submitted by the form?
    #if request.params.get('submit', False):
    if len(request.params):
        recipients = request.db_session.query(Setting)\
                 .filter(Setting.name.like(u'contact_dst_email_%')).all()

        if len(recipients) == 0:
            # no need to send anything to anyone
            ctx.result_message = _(u"Grazie per averci contattato. " +\
                                   u"Le risponderemo al più presto.")
            return

        log.debug("Recipients: %s", recipients)
        log.debug("Form has been submitted, validating fields")
        validate_name(request, ctx.name, 'name')
        validate_name(request, ctx.surname, 'surname')
        validate_captcha(request)

        if not email_re.match(ctx.email):
            ctx.error['email'] = _(u"Inserisci un indirizzo email valido.")
            ctx.success = False

        if not phone_re.match(ctx.phone):
            ctx.error['phone'] = _(u"Inserisci un numero di telefono valido.")
            ctx.success = False

        if len(ctx.message) < 10:
            ctx.error['message'] = _(u"Inserisci almeno 10 caratteri.")
            ctx.success = False

        if not ctx.agreement == 'on':
            ctx.error['agreement'] = _(u"Devi accettare i termini di Privacy")
            ctx.success = False

        # FIXME: use a template!
        body = u"Nome : %s \n" % (ctx.name)
        body = u"%sCognome : %s \n" % (body, ctx.surname)
        body = u"%sTelefono : %s \n\n" % (body, ctx.phone)

        for key, value in request.params.iteritems():
            if key not in form_keys and not key.startswith("recaptcha"):
                p = key.decode('utf8')
                body = u"%s%s : %s \n" % (body, p.title(), value)
                ctx.vars[key] = value

        body = u"%sMessaggio : \n%s\n" % (body, ctx.message)

        mailer = get_mailer(request)
        message = Message(subject=u"Nuovo messaggio dal form di contatto web",
                          sender=ctx.email,
                          body=body,
                          recipients=[r.value for r in recipients[0:1]],
                          cc=[r.value for r in recipients[1:]])

        if ctx.success:
            log.debug('Form is valid, sending emails')
            try:
                mailer.send_immediately(message, fail_silently=False)
                ctx.result_message = _(u"Grazie per averci contattato. " +\
                                     u"Le risponderemo al più presto.")
            except  Exception:
                log.exception("Errore nell'invio del messaggio. \n")
                ctx.result_message = _(u"Errore nell'invio del messaggio. " +\
                                     u"Si prega di riprovare più tardi.")
                ctx.success = False
        else:
            ctx.result_message = _(u"Errore nell'invio del form. "
                                 "Ricontrollare i campi e riprovare.")

        log.debug("Success: %s", ctx.success)
        log.debug("Message: %s", ctx.result_message)
        log.debug("Errors: %s", ctx.error)
