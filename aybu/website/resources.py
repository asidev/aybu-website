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

import logging
from collections import namedtuple
from pyramid.httpexceptions import HTTPNotFound
from aybu.core.models import Language, PageInfo
from sqlalchemy.orm.exc import NoResultFound


__all__ = []

log = logging.getLogger(__name__)


UrlPart = namedtuple('UrlPart', ['part', 'resource'])


def get_root_resource(request):

    path_info = request.path_info
    log.debug('get_root_resource: %s', path_info)

    # Getting url_parts and for each part associating a Resource
    # On request.path_info applying strip('/') remove the initial / so
    # with the following split('/') we obtain a list just with parts
    url_parts = [UrlPart(part=url_part, resource=Resource())
                 for url_part in path_info.strip('/').split('/')
                 if url_part]

    log.debug('url_parts: %s', url_parts)

    if not url_parts:
        # URL is '/'.
        log.debug('Return NoLanguage context.')
        return NoLanguage()

    if url_parts[0].part == 'admin':
        log.debug("In admin panel, removing admin")
        url_parts = url_parts[1:]
        path_info = path_info.replace('/admin', '')

    language = Language.get_by_lang(request.db_session,
                                            url_parts[0].part)
    request.language = language
    if language is None:
        # language not found, return a 404
        log.debug("No language found")
        raise HTTPNotFound()

    if len(url_parts) == 1:
        # URL is like '/{lang}'.
        log.debug('Get Context by Language %s.', url_parts[0].part)
        url_parts[0] = UrlPart(part=url_parts[0].part,
                               resource=request.language)

    else:
        # URL is like '/{lang}/{node}/[...]/{page}[.ext]
        # Get the NodeInfo from database using path_info.
        log.debug('Get Context by NodeInfo %s.', path_info)
        try:
            url_parts[-1] = UrlPart(part=url_parts[-1].part,
                                    resource=PageInfo.get_by_url(
                                                        request.db_session,
                                                        path_info)
                                )
        except NoResultFound:
            return HTTPNotFound()

    # Create the resources tree.
    # The last element in resources tree is the request context.
    tmp = root = Resource()
    for url_part, resource in url_parts:
        tmp[url_part] = resource
        tmp = tmp[url_part]

    log.debug('The root resource is: %s', root)

    return root


class NoLanguage(object):
    """ This class is the context when no language nor nodes are specified."""
    pass


class Resource(dict):
    """
        This class is a basic resource.
        it is needed to build ACL, do NOT use for requests context!
    """
    pass
