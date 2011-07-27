#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
from aybu.website.models.language import Language
from aybu.website.models.node import NodeInfo
import logging


__all__ = []

log = logging.getLogger(__name__)


UrlPart = namedtuple('UrlPart', ['part', 'resource'])


def get_root_resource(request):

    log.debug('get_root_resource: %s', request.path_info)

    # Getting url_parts and for each part associating a Resource
    # On request.path_info applying strip('/') remove the initial / so
    # with the following split('/') we obtain a list just with parts
    url_parts = [UrlPart(part=url_part, resource=Resource())
                 for url_part in request.path_info.strip('/').split('/')
                 if url_part]

    log.debug('url_parts: %s', url_parts)

    if not url_parts:
        # URL is '/'.
        log.debug('Return NoLanguage context.')
        return NoLanguage()

    request.language = Language.get_by_lang(request.db_session,
                                            url_parts[0].part)

    if len(url_parts) == 1:
        # URL is like '/{lang}'.
        log.debug('Get Context by Language %s.', url_parts[0].part)
        url_parts[0] = UrlPart(part=url_parts[0].part,
                               resource=request.language)

    else:
        # URL is like '/{lang}/{node}/[...]/{page}[.ext]
        # Get the NodeInfo from database using path_info.
        log.debug('Get Context by NodeInfo %s.', request.path_info)
        url_parts[-1] = UrlPart(part=url_parts[-1].part,
                                resource=NodeInfo.get_by_url(
                                                    request.db_session,
                                                    request.path_info)
                               )

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
