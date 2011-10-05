#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.website.models import Language
from babel import Locale


def get_negotiated_language(request):
    """ This function returns a Language from database that
        best matches one of those requested by the client.
        If a match cannot be found, it simply returns the first
        language available
    """

    # Get all the registered and enabled languages of the system.
    available = [str(locale)
                 for locale in Language.get_locales(request.db_session,
                                                    enabled=True)]
    # Get client preferred languages.
    preferred = [str(locale) for locale in request.accepted_locales]

    # Choose the best one.
    negotiated = Locale.negotiate(preferred, available)
    if negotiated is None:
        lang = available[0][:2]
    else:
        lang = negotiated.language

    return Language.get_by_lang(request.db_session, lang)
