__version__ = '0.1.0'


def setup(app, config=None):
    if not config:
        from aiowebapi.config import config
    app.add_routes(config.routes)
    for subapp in config.apps:
        app.add_subapp(subapp)
    app.middlewares.extend(config.middlewares)

