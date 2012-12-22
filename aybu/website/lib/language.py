#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010-2012 Asidev s.r.l.

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

from aybu.core.models import Language
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
