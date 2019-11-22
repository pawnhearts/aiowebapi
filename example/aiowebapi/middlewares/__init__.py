import inspect
from functools import partial

from aiohttp import web

from aiowebapi.utils import dumps
from pydantic import BaseModel, create_model

@web.middleware
async def webapi_error_middleware(request, handler):
    try:
        response = await handler(request)
        status = response.status
        if response.status != 404:
            return response
        message = response.message
    except web.HTTPException as ex:
        # if ex.status != 404:
        #     raise
        message = ex.reason
        status = ex.status
    return web.json_response({'error': message}, status=status)


@web.middleware
async def webapi_validate_query(request, handler):
    import pdb
    pdb.set_trace()
    self = handler.__closure__[0].cell_contents.__self__
    if request.method not in ('GET', 'POST', 'PUT', 'DELETE'):
        raise web.HTTPMethodNotAllowed(f'{request.method} not allowed')
    query = request.query.copy()
    if self.paginator:
        self.paginator.get_page_from_query(query)
    if self.filter_class:
        self.filter = self.filter_class(**request.query)
    validated_query = self.query_schema(**query.items()).dict()
    result = await handler(request, **request.match_info, **validated_query)
    return web.json_response(result, dumps=dumps)

middlewares = [webapi_error_middleware, webapi_validate_query]

