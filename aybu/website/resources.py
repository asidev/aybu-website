#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging


__all__ = []

log = logging.getLogger(__name__)


class NoLanguage(object):
    """ This class is the context when no language nor nodes are specified."""
    pass


def get_root_resource(request):

    log.debug('get_root_resource: %s', request.path_info)

    url_parts = [url_part
                 for url_part in request.path_info.strip('/').split('/') 
                 if url_part]

    log.debug('url_parts: %s', url_parts)

    if not url_parts:
        # URL is '/'.
        log.debug('Return NoLanguage context.')
        return NoLanguage()

    lang = url_parts.pop(0)

    if not url_parts:
        # URL is like '/{lang}'.
        #criterion = Language.lang.ilike(lang)
        #query = request.db_session.query(Language).filter(criterion)
        return {lang: lang}#query.first()}

    resource = {}
    resource[lang] = {}

    # for user, address in session.query(User, adalias).join(adalias, User.addresses):
    queries = []
    pivot = resource[lang]

    for url_part in url_parts:

        pivot[url_part] = {}
        pivot = pivot[url_part]

        #criterion = and_(NodeInfo.url_part.ilike(url_part),
        #                 NodeInfo.lang.has(NodeInfo.lang.ilike(lang)))
        #query = request.db_session.query(NodeInfo).filter(criterion)
        #NodeInfoAlias = aliased(NodeInfo, query.subquery())
        #query = request.db_session.query(Node).join(NodeInfoAlias, Node.translations)

    log.debug(resource)

    if url_parts:
        nodes = url_parts

    return resource
