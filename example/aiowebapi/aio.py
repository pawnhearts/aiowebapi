import asyncio
import json
from functools import wraps
from typing import Optional, Dict, List

import typing
from aiohttp import web
from aiohttp.web_exceptions import HTTPMethodNotAllowed, HTTPNotFound
from bson import ObjectId

from pydantic import BaseModel, create_model
import math
from enum import Enum
import inspect
import aiohttp_autoreload
import aiohttp_debugtoolbar
from db import Database

routes = web.RouteTableDef()
page_size = 20




class RequestSchema(BaseModel):
    # page: Optional[int] = 1
    features: Optional[Enum('Feature', ['a'])]
    # meals: Enum('Meal', ['a'])
    # cuisine: Enum('cuisine', ['a'])
    # type: Enum('cuisine', ['a'])

    def query(self):
        return {k: v for k, v in self.dict().items() if v is not None}









class Serializer(BaseModel):
    _id: Optional[ObjectId]
    id: Optional[int]
    name: Optional[str]
    photos: Optional[List]
    tr_rating: Optional[str]
    ta_rating: Optional[str]
    num_reviews: Optional[int]
    prices: Optional[str]
    open_time: Optional[List]
    distance: Optional[int]
    address: Optional[str]
    type: Optional[List]
    users: Optional[List]
    phone: Optional[str]
    features: Optional[List]
    cuisine: Optional[List]
    menu: Optional[str]
    map: Optional[str]
    statistics: Optional[Dict]
    # def __init__(self, **kwargs):
    #     self.data = kwargs
    #     for k, v in kwargs.items():
    #         t = type(v).__name__
    #         if t in ['list', 'dict']:
    #             t = t.title()
    #         print(f'{k}: Optional[{t}]')
    # def dict(self):
    #     return self.data




class My(ApiView):

    filter_class = RequestSchema

    async def get(self, request, pk):
        obj = await self.get_object(int(pk))
        if not obj:
            raise HTTPNotFound
        return self.serializer_class(**obj).dict()

    async def list(self, request):
        data = await self.paginate()
        return data





async def hello(request):
    q = dict(request_schema.load(request.query))
    page_num = q.get('page', 1)
    skips = page_size * (page_num - 1)
    if 'page' in q:
        q.pop('page')

    total = await app.col.count(q)
    pages = math.ceil(total / page_size)

    data = await app.col.find(q).batch_size(10).skip(skips).limit(page_size).to_list()
    for d in data:
        d.pop('_id')

    return web.json_response({'pages': pages, 'current': page_num, 'locations': data})



async def init(loop):
    app = web.Application()
    # aiohttp_debugtoolbar.setup(app)
    aiohttp_autoreload.start()
    #app.add_routes(routes)
    #app.on_startup.append(on_startup)
    #app.router.add_get('/', hello)
    db = await Database.init(loop)
    col = db.restaurants
    RequestSchema.__annotations__['features'] = Optional[Enum('Feature', await col.distinct('features'))]
    meals = await col.distinct('meals')
    type = await col.distinct('type')
    app.add_routes(My().get_routes())
    return app


def main():
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init(loop))
    web.run_app(app)

if __name__ == '__main__':
    main()
