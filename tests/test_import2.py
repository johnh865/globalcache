# -*- coding: utf-8 -*-

from globalcache import gcache




@gcache.decorate(size_limit=10)
def expensive_func10(i: int):
    """Dummy function, prints input."""
    print(i)
    return i



@gcache.decorate
class Jimmy:
    def __init__(self, x: int):
        self.x = x
        print('hello')
       
        