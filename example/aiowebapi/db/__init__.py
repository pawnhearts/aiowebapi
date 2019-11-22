import aiomongo


class Database:
    client = None
    db = None

    @classmethod
    async def init(cls, loop):
        cls.client = await aiomongo.create_client('mongodb://localhost:27017/truerating?w=2&maxpoolsize=10', loop=loop)
        cls.db = cls.client.get_default_database()
        return cls.db

    def __getattr__(self, item):
        return getattr(self.db, item)

    def __getitem__(self, item):
        return getattr(self.db, item)


Database = Database()


async def setup_db():
    return
