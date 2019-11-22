from aiowebapi import views


class ExampleApi(views.ApiView):
    path = '/'

    def get(self, request, pk):
        return {'pk': pk}

    def list(self, request, q: str=''):
        collection = ['aaaa', 'bbb', 'ccc']
        return [c for c in collection if q in c]
