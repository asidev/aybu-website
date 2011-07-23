#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.website.models.language import Language
#from aybu.website.models.node import NodeInfo
import logging


__all__ = []

log = logging.getLogger(__name__)


def get_root_resource(request):

    log.debug('get_root_resource: %s', request.path_info)

    url_parts = [(url_part, Resource())
                 for url_part in request.path_info.strip('/').split('/') 
                 if url_part]

    log.debug('url_parts: %s', url_parts)

    if not url_parts:
        # URL is '/'.
        log.debug('Return NoLanguage context.')
        return NoLanguage()

    if len(url_parts) == 1:
        # URL is like '/{lang}'.
        log.debug('Return Language %s (if exists) or None.', lang)
        return Language.get_by_lang(request.db_session, url_parts[0])

    else:
        # URL is like '/{lang}/{node}/[...]/{page}[.ext]
        # Get the NodeInfo from database using path_info.
        url_parts[-1] = (url_parts[-1][0], 0)
                         #NodeInfo.get_by_url(request.db_session,
                         #                    request.path_info))

    # Create the resources tree.
    # The last element in resources tree is the request context.
    tmp = root = {}
    for url_part, resource in url_parts:
        tmp[url_part] = resource
        tmp = tmp[url_part]
        key = url_part

    log.debug('Resource is: %s', root)
    log.debug('Pivot is: %s', tmp)
    log.debug('Key is: %s', key)

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
