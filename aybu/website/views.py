def show_node(request):

    language = request.matchdict['language']
    nodes = request.matchdict['nodes']
    url = request.route_url('show_node', language=language, nodes=nodes)

    return dict(language=language, nodes=nodes, url=url)
