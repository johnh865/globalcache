# -*- coding: utf-8 -*-

from globalcache import gcache
from tests.example_import import Jimmy
# 
gcache.init(globals())
# gcache.reset()

@gcache.decorate
def expensive_func11(i: int):
    """Dummy function, prints input."""
    print(i)
    return i


Jimmy(1)
Jimmy(2)
Jimmy(3)
