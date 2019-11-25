import aiomongo


class Database:
    client = None
    db = None
    url = None

    def __init__(self, url):
        self.url = url

    @classmethod
    async def init(cls, loop):
        cls.client = await aiomongo.create_client(self.url, loop=loop)
        cls.db = cls.client.get_default_database()
        return cls.db

    def __getitem__(self, item):
        return getattr(self.db, item)

    async def query(self, table):
        return Query(getattr(self.db, table))


class Query:
    def __init__(self, col):
        self.col = col
    async def get(self, **kwargs):
        res = await self.col.filter(**kwargs).limit(1).to_list()
        return res[0] if res else None
    def filter(self, **kwargs):
        return self.col.find(kwargs)
    def __getitem__(self, item):
        col = self.col
        if isinstance(item, slice):
            if slice.start:
                col = col.skip(slice.start)
            if slice.stop:
                col = col.limit(slice.stop)
        else:
            raise NotImplementedError
        return col
    async def count(self):
        return await self.col.count()
    async def list(self):
        return await self.col.to_list()


