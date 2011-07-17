from pyramid.config import Configurator
from aybu.website.resources import Root

def main(global_config, **settings):

    config = Configurator(root_factory=Root, settings=settings)

    add_routes(config)
    add_views(config)
    add_static_views(config)

    return config.make_wsgi_app()


def add_routes(config):

    config.add_route('show_node', '/{language}/*nodes')

    return config


def add_views(config):

    config.add_view('aybu.website.views.show_node',
                    renderer='aybu.website:templates/show_node.mako',
                    route_name='show_node')

    return config


def add_static_views(config):

    config.add_static_view('static', 'aybu.website:static')

    return config
