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
from aybu.core.authentication import Authenticated
from pyramid.security import (Allow,
                              Everyone,
                              ALL_PERMISSIONS)


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

    need_auth = False
    if url_parts[0].part == 'admin':
        log.debug("In admin panel, removing admin")
        url_parts = url_parts[1:]
        path_info = path_info.replace('/admin', '')
        need_auth = True

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
            # Remove '.ext' from the url.
            url_parts[-1] = url_parts[-1].part.rsplit('.', 1)[0]
            resource = PageInfo.get_by_url(request.db_session,
                                           path_info.rsplit('.', 1)[0])
            url_parts[-1] = UrlPart(part=url_parts[-1], resource=resource)
        except NoResultFound:
            return HTTPNotFound()

    # Create the resources tree.
    # The last element in resources tree is the request context.
    tmp = root = Resource()
    parent = None
    acl = [(Allow, Everyone, ALL_PERMISSIONS)]
    if need_auth:
        acl = Authenticated.__acl__

    for url_part, resource in url_parts:
        resource.__parent__ = parent
        resource.__acl__ = acl
        parent = resource
        tmp[url_part] = resource
        tmp = tmp[url_part]
        log.debug("Resource: %s, acl: %s, parent: %s",
                  resource, resource.__acl__, resource.__parent__)

    return root


class NoLanguage(object):
    """ This class is the context when no language nor nodes are specified."""
    pass


class Resource(dict):
    """
        This class is a basic resource.
        it is needed to build ACL, do NOT use for requests context!
    """
