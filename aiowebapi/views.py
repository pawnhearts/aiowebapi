from functools import wraps

from aiohttp import web
from aiohttp.web_exceptions import HTTPMethodNotAllowed

from aiowebapi.config import config
from aiowebapi.pagination import Paginator
from aiowebapi.utils import get_query_schema, dumps

DEFAULT_METHODS = ('GET', 'POST', 'PUT', 'DELETE')


class ApiViewMeta(type):
    def __new__(cls, name, bases, dct):
        for k in ['get', 'list', 'post', 'patch', 'put', 'delete']:
            if k in dct:
                dct[k].query_schema = get_query_schema(dct[k])
        return super().__new__(cls, name, bases, dct)


def handler_decorator(func):
    self = func.__self__
    async def wrapper(request):
        query = request.query.copy()
        if self.paginator:
            self.paginator.get_page_from_query(query)
        if self.filter_class:
            self.filter = self.filter_class(**request.query)
        validated_query = func.query_schema(**query).dict()
        result = await func(request, **request.match_info, **validated_query)
        return web.json_response(result, dumps=dumps)
    return wrapper


class ApiView(metaclass=ApiViewMeta):

    filter_class = None
    paginator_class = Paginator
    serializer_class = None
    table = None
    filter = None
    page_size = config.DEFAULT_PAGE_SIZE
    path = '/'
    id_field: int = 'id'

    def __init__(self):
        if self.paginator_class:
            self.paginator = self.paginator_class(self.page_size, self.serializer_class)
        else:
            self.paginator = None
        if not self.path.endswith('/'):
            self.path = '{}/'.format(self.path.strip())

    def query(self, q=None):
        params = {}
        if self.filter:
            params.update(self.filter.query())
        if q:
            params.update(q)
        return config.db.query(self.table).filter(**params)

    async def paginate(self, query=None):
        if query is None:
            query = self.query()
        return await self.paginator.paginate(query=query, page=self.page)

    async def dispatch(self, request):
        self.request = request
        if request.path == self.path and request.method == 'GET':
            method = self.list
            many = True
        else:
            method = getattr(self, request.method.lower())
            many = False
        if not method:
            raise HTTPMethodNotAllowed('', DEFAULT_METHODS)
        if many:
            if 'page' in request.query:
                self.page = int(request.query['page'])
            else:
                self.page = 1
            if self.filter_class:
                self.filter = self.filter_class(**request.query)
        result = await method(request)
        return web.json_response(result, dumps=dumps)

    def get_routes(self):
        routes = []
        if self.__annotations__['id_field'] == int:
            regex = r':\d+'
        else:
            regex = ''
        if hasattr(self, 'list'):
            routes.append(web.get(self.path, handler_decorator(self.list)))
            # routes.append(web.route('*', self.path, self.dispatch))
        if hasattr(self, 'post'):
            routes.append(web.post(self.path, handler_decorator(self.post)))
        if hasattr(self, 'get'):
            # routes.append(web.route('*', self.path+r'{pk:\d+}', self.dispatch))
            routes.append(web.get(f'{self.path}{{pk{regex}}}', handler_decorator(self.get)))
        if hasattr(self, 'put'):
            routes.append(web.put(f'{self.path}{{pk{regex}}}', handler_decorator(self.put)))
        if hasattr(self, 'delete'):
            routes.append(web.delete(f'{self.path}{{pk{regex}}}', handler_decorator(self.delete)))
        return routes

    async def get_object(self, pk):
        cast = self.__annotations__['id_field']
        return await config.db.query(self.table).get(**{self.id_field: cast(pk)})
