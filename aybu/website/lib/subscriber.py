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

from aybu.website.lib.helper import TemplateHelper

def add_renderer_globals(event):
    if hasattr(event['request'], "template_helper"):
        h = event['request'].template_helper
        del event['request'].template_helper
    else:
        h = TemplateHelper(event['request'])

    event['_'] = event['request'].translate
    event['localizer'] = event['request'].localizer
    event['h'] = h
    event['c'] = h

def context_found(event):
    event.request.template_helper = TemplateHelper(event.request)
