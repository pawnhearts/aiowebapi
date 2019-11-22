from aiowebapi.config import BaseConfig


class LocalConfig(BaseConfig):
    DATABASES = {'default': 'mongodb://localhost:27017/truerating?w=2&maxpoolsize=10'}
    ROOT_URLS_CONIFG = 'urls'

