import inspect
import json

from pydantic import create_model


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def dumps(*args, **kwargs):
    kwargs['cls'] = JSONEncoder
    return json.dumps(*args, **kwargs)


def get_query_schema(handler):
    params = inspect.signature(handler).parameters
    query_params = {k: (p.annotation, p.default) for k, p in params.items() if k not in ('pk', 'request', 'self')}
    return create_model('query_schema', **query_params)
