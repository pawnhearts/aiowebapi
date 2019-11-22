import importlib

from aiohttp import web


class WebApiApplication(web.Application):
    def __init__(self, *args, **kwargs):
        try:
            middlewares = importlib.import_module('.middlewares', __package__)
            kwargs['middlewares'] = middlewares.middlewares
        except ModuleNotFoundError:
            pass
        app = super().__init__(*args, **kwargs)
        try:
            urls = importlib.import_module('.urls', __package__)
            app.add_routes(urls.routes)
        except ModuleNotFoundError:
            pass

        for singal_name in ('startup', 'response_prepare', 'shutdown', 'cleanup`'):
            if hasattr(self, singal_name):
                getattr(app, f'on_{singal_name}').append(getattr(self, singal_name))

