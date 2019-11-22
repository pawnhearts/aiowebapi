from aiohttp import web

from aiowebapi import setup

from config import LocalConfig

LocalConfig.setup()

app = web.Application()
setup(app, LocalConfig)
# from views import ExampleApi
# print(ExampleApi().get)
# app.add_routes([web.get('/foo', ExampleApi().list)])
web.run_app(app)
