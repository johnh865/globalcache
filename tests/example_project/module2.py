# -*- coding: utf-8 -*-

from globalcache import Cache
from math import sqrt

gcache = Cache(globals())


class Class2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        
        
        
    def __repr__(self):
        x = repr(self.x)
        y = repr(self.y)
        return f'Class2({x},{y})'
    
    @gcache.decorate
    def add(self):
        return self.x + self.y
    
    @gcache.decorate
    def power(self, n: float):
        return (self.x + self.y) ** n
    
    
    