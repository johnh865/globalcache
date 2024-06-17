# -*- coding: utf-8 -*-
import logging


logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

from globalcache import Cache
from tests.test import Capturing


def test_class():

    logger.debug('#1  Initializing the Cache')
    gcache = Cache(globals())
    gcache.reset()
    
    
    logger.debug('#2 Creating Class')
    class MyClass:
        def __init__(self, a: int):
            self.a = a
            
        
        def __repr__(self):
            return f'MyClass({self.a!r})'
            
        # def __hash__(self):
        #     return hash('MyClass(' + str(self.a) + ')')
        
        
        # def __eq__(self, other):
        #     return hash(self) == hash(other)
        
        
        logger.debug('#3 Creating the cached method')
        @gcache.decorate
        def calc(self, b: int):
            print('calc', b)
            return self.a + b
        
        
    logger.debug('#4 Create MyClass(1)')
    class1 = MyClass(1)
    class2 = MyClass(2)
    class3 = MyClass(1)
    
    logger.debug('#5 Call method class1.calc(2)')
    with Capturing() as output1:
        class1.calc(2)
        class3.calc(2)
        class3.calc(2)
        class3.calc(2)
        class3.calc(2)
    print(output1)
    assert len(output1) == 1
    assert output1[0] == 'calc 2'


        
    
if __name__ == '__main__':   
    test_class()
# fcache = class1.calc.fn_cache.fcache
# print('')
# print('')
# print('Entries in fcache:')
# for key, value in fcache:
#     print(key)
#     print(value)
#     print('')
# keys = list(fcache.keys())

# print('FCACHE')
# print(gcache.function_caches)

# print('')
# print(gcache.global_singleton.global_dict)

