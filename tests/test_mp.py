# -*- coding: utf-8 -*-

"""Test multiprocessing and multithreading."""
import logging 
import sys
from io import StringIO 

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logger.debug('MILESTONE #1')

from globalcache import Cache
from multiprocessing import Pool, Queue
from concurrent.futures import ProcessPoolExecutor


class Capturing(list):
    """Capture stdout.
    https://stackoverflow.com/questions/16571150/how-to-capture-stdout-output-from-a-python-function-call"""
    
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout



logger.debug('MILESTONE #2')
gcache = Cache(globals())

logger.debug('MILESTONE #3')
gcache.delete_shelve()





logger.debug('MILESTONE #4')
@gcache.decorate(write=False)
def func1(x,):
    print(f'func1({x})')
    logger.debug(f'Calling function {x}')
    # queue.put(x)
    return x


# @gcache.decorate(save=True)
# def func2(x):
#     logger.debug('FUNC2 CALL')
#     print(f'func2({x})')
#     return x

logger.debug('MILESTONE #5')
def test_mp1():
    
    # q1 = Queue()
    

    logger.debug('MILESTONE #6')
    args = [1,2,1,2]      
    # args2 = [q1, q1, q1, q1]

    
    # with ProcessPoolExecutor(2) as p:
    #     output = list(p.map(func1, args,))
    
    with Pool(2) as p:
        logger.debug('Creating POOL')
        output = p.map(func1, args)
    
    p.join()
    logger.debug('MILESTONE #6.5')
    
    # sys.stdout.flush()
    # print('Captured')
    # print(output1)
    # breakpoint()
    breakpoint()
    # print('ehhlljk')
    return

logger.debug('MILESTONE #7')
        

if __name__ == '__main__':
    logger.debug('MILESTONE #8')

    test_mp1()
    logger.debug('MILESTONE #9')
