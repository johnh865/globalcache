# -*- coding: utf-8 -*-

from globalcache import gcache
from tests.test_import2 import Jimmy, expensive_func10
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