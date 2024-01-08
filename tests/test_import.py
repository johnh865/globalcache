# -*- coding: utf-8 -*-

from globalcache import Cache

gcache = Cache(globals())

@gcache.decorate(size_limit=10)
def expensive_func10(i: int):
    """Dummy function, prints input."""
    print(i)
    return i

