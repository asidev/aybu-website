def my_view(context, request):

    language = None
    nodes = None
    url = None

    return dict(language=language, nodes=nodes, url=url)


def favicon(context, request):
    return dict()


def sitemap(context, request):
    return dict()


def robots(context, request):
    return dict()


def show_not_found_error(context, request):
    return dict()
