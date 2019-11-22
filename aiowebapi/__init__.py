__version__ = '0.1.0'
from .db import setup_db


def setup(app, config=None):
    if not config:
        from aiowebapi.config import config
    app.add_routes(config.routes)
    #app.on_startup.append(setup_db)
    for subapp in config.apps:
        app.add_subapp(subapp)
    app.middlewares.extend(config.middlewares)

