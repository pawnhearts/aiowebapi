from aiohttp import web


class Paginator:
    page_query_param = 'page'

    def __init__(self, page_size, serializer):
        self.page_size = page_size
        self.serializer = serializer

    async def paginate(self, query, page=1):
        self.page = page
        self.total = await query.count()
        self.pages = math.ceil(self.total / page_size)
        skips = page_size * (self.page - 1)
        self.data = await query.skip(skips).limit(page_size).to_list()
        if self.serializer:
            self.data = [self.serializer(**rec).dict() for rec in self.data]
        return self.page_data(self.data)

    def page_data(self, data):
        return {'pages': self.pages, 'page': self.page, 'data': data}

    def get_page_from_query(self, query):
        page = '1'
        if self.page_query_param in query:
            page = query.pop(self.page_query_param)
        if page.isnumeric():
            page = int(page)
        else:
            page = -1
        if page <= 0:
            raise web.HTTPBadRequest(f'Bad page nunber: {page}')
        self.page = page


