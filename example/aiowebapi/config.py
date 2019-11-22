import os
import importlib
from proxy_tools import Proxy


class BaseConfig:
    _configured = False
    _routes = []
    _apps = []
    DEFAULT_PAGE_SIZE = 50
    DATABASES = {'default': ''}
    URLS = 'urls'
    APPS = []
    MIDDLEWARES = ['aiowebapi.middlewares']

    @classmethod
    def setup(cls):
        if cls == BaseConfig:
            raise Exception(f'Improperly configured. You should subclass {cls.__name__}')
        if cls._configured:
            return
        config_module.config_module = cls
        for k, v in os.environ.items():
            if hasattr(cls, k):
                if v.isnumberic():
                    v = int(v)
                setattr(cls, k, v)
        urls = importlib.import_module(cls.ROOT_URLS_CONIFG)
        cls.routes = urls.routes
        cls.apps = [importlib.import_module(app) for app in cls.APPS]
        cls.middlewares = []
        for middleware_module in map(importlib.import_module, cls.MIDDLEWARES):
            cls.middlewares.extend(middleware_module.middlewares)
        cls._configured = True


def config_module():
    if hasattr(config_module, 'config_module'):
        return config_module.config_module
    if module_name := os.environ.get('__config_module__'):
        config_module.config_module = importlib.import_module(module_name)
        config_module.config_module.setup()
    else:
        raise Exception('Improperly configured')

    return config_module.config_module


config = Proxy(config_module)
