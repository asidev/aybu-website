#!/usr/bin/env python
# -*- coding: utf-8 -*-

def add_renderer_globals(system):
    request = system['request']    
    return {'_': request.translate, 'localizer': request.localizer}

