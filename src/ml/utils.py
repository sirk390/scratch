

class Object(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
    def __getattr__(self, key):
        return self.kwargs[key]
