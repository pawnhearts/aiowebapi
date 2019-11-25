from aiohttp import web


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


middlewares = []#webapi_error_middleware]

