# -*- coding: utf-8 -*-

import sys
from io import StringIO 
import globalcache
from globalcache import Cache, Settings, CacheError
import logging


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
        
        
            
def expensive_func():
    """An arbitrary function to be evaluated by globalcache with output 10"""
    for ii in range(5):
        print('Meow', ii)
    return 10.0


def expensive_func2():
    """An arbitrary function to be evaluated by globalcache with output 20"""
    for ii in range(5):
        print('Ouch', ii)
    return 20.0


def expensive_func3(a : str):
    """Dummy function, prints input."""
    print(a)
    return a*2

def expensive_func4(i: int):
    """Dummy function, prints input."""
    print(i)
    return i*10


def expensive_func5(i: int):
    """Dummy function, prints input."""
    print(i)
    return i*100




def caller1():
    c = Cache(globals())
    
    cvar = c.var('test', )
    if cvar.not_cached:
        print('calculating')
        out = expensive_func()
        cvar.set(out)
    out = cvar.get()
    assert out == 10

    cvar = c.var('meow')
    if cvar.not_cached:
        print('calculating')
        out = expensive_func2()
        cvar.set(out)
    out = cvar.get()
    assert out == 20


def test_caller():
    cache = Cache(globals(), reset=True)
    with Capturing() as output1:
        caller1()
        
    with Capturing() as output2:
        caller1()
        
    assert len(output1) == 12
    assert len(output2) == 0
    return
    

def test_decorator():
    
    c = Cache(globals(), reset=True)
    
    @c.decorate
    def expensive_func():
        for ii in range(5):
            print('Meow', ii)
        return 10.0
    
    
    with Capturing() as output1:
        out = expensive_func()
        assert out == 10
    
    with Capturing() as output2:
        out = expensive_func()
        assert out == 10
    assert len(output1) == 5
    assert len(output2) == 0
    return


def test_repeated_names():
    """Test repeated variable names. Should raise ValueError"""
    
    c = Cache(globals(), reset=True)
    cvar = c.var('test1')
    try:
        cvar = c.var('test1')
    except CacheError:
        print('Good')
    else:
        assert False
        
        
def test_arg_cache():
    """Make sure cache doesn't exceed limit."""
    cache = Cache(globals(), reset=True)
    size = 5
    for ii in range(10):
        cache = Cache(globals(), reset=False, size_limit=size)
        
        cvar = cache.var('a', args=(ii))
        cvar.set(ii)
        
        alen = len(cvar.fn_cache.fcache)
        assert alen <= size
        # breakpoint()
        # print(ii, alen, min(ii+1, size) )
        assert alen == min(ii+1, size)        
    return


def test_default_cache_size():
    
    c = Cache(globals(), reset=True)
    # size = Settings.size_limit
    size = globalcache.cache.DEFAULT_SIZE_LIMIT
    
    
    for ii in range(10):
        c = Cache(globals(), reset=False)
        
        cvar = c.var('a', args=(ii))
        cvar.set(ii)
        
        alen = len(cvar.fn_cache.fcache)
        assert alen <= size
        assert alen == min(ii+1, size)        
    return    
    
    
def test_settings_size():
    """Test that SIZE_LIMIT actually sets the global size limit."""
    Settings.size_limit = 50
    c = Cache(globals(), reset=True)
    
    
    for ii in range(100):
        cache = Cache(globals(), reset=False)
        cvar = cache.var('a', args=(ii))
        cvar.set(ii)
                
        alen = len(cvar.fn_cache.fcache)
        print(ii, alen)
        # breakpoint()
        assert alen == min(ii+1, Settings.size_limit)      
    
    # Reset settings back to normal
    Settings.size_limit = None
        
    return


def test_settings_disable():
    """Test to make sure DISABLE actually disables cache."""
    Settings.disable = True
    
    with Capturing() as output1:
        caller1()
        
    with Capturing() as output2:
        caller1()
    
    assert len(output1) == 12
    assert len(output2) == 12
    Settings.disable = False

    return
    

def test_arguments():
    Settings.diable = False
    cache = Cache(globals(), reset=True)
    
    decorator = cache.decorate(size_limit=1000)
    func_cached = decorator(expensive_func3)
    
    logger.info('STEP 1: FIRST SET VALUES')
    with Capturing() as output1:
        func_cached('a')        
        func_cached('b')    
    logger.info('output1:')         
    logger.info(output1)
    assert output1[0] == 'a'
    assert output1[1] == 'b'
    
    logger.info('STEP 2: RETRIEVE')
    with Capturing() as output2:
        out1 = func_cached('a')        
        out2 = func_cached('b')     
        out3 = func_cached('c')
    logger.info('output2:')         
    logger.info(output2)
    logger.info('....')
    
    assert output2[0] == 'c'
    assert out1 == 'aa'
    assert out2 == 'bb'
    assert out3 == 'cc'
    

def test_arguments2():
    cache = Cache(globals(), reset=True)
    decorator = cache.decorate(size_limit=50)
    decorator2 = cache.decorate(size_limit=5)
    
    
    func_cached = decorator(expensive_func4)
    func_cached2 = decorator2(expensive_func5)
    
    with Capturing() as output1:
        for i in range(50):
            func_cached(i)
    logger.info('....')
    
    with Capturing() as output2:
        for i in range(60):
            out = func_cached(i)
    logger.info('....')
            
            
    with Capturing() as output3:
        for i in range(50):
            func_cached2(i)
    logger.info('....')
    
    with Capturing() as output4:
        for i in range(50, -1, -1):
            out = func_cached2(i)



def test_reset_cache():
    cache = Cache(globals())
    cache.reset()
    
    @cache.decorate
    def expensive_func(x):
        print('Meow', x)
        return x*2    
    
    with Capturing() as output1:
        expensive_func(1)
        expensive_func(2)
        expensive_func(3)
    
    fc = expensive_func.fn_cache
    assert len(fc.fcache) == 3
    assert len(output1) == 3
    
    # Reset the cache
    cache.reset()
    # assert len(fc.fcache) == 0
    
    with Capturing() as output2:
        expensive_func(1)
        expensive_func(2)
        expensive_func(3)
    # breakpoint()
    
    assert len(output2) == 3
    
    
    
def test_save_cache():
    cache = Cache(globals(), size_limit = 10)

    
    @cache.decorate(save=True)
    def expensive_func(x):
        for ii in range(5):
            print('Meow', ii)
        return x*2
    
    # Delete existing shelve if it exists
    cache.delete_shelve()
    cache.reset()
    
    # Capture print output, only occurs if no cache
    with Capturing() as output1:
        expensive_func(1)
        expensive_func(1)
    
    assert len(output1) == 5
    
    # Delete globals(). Because of save, shelve data should exist
    cache.reset()
    
    # No output should print because of shelve cache
    with Capturing() as output2:
        expensive_func(1)
    
    assert len(output2) == 0
    
    # Delete the shelve again. We should see output print
    cache.reset()
    cache.delete_shelve()
    with Capturing() as output3:
        expensive_func(1)
        
    assert len(output3) == 5
    
    # cleanup
    cache.delete_shelve()


def test_cache_import():
    """Import cache from another module. Test set_globals method."""
    from tests.test_import import expensive_func10, gcache
    import numpy as np
    
    gcache.set_globals(globals())
    
    with Capturing() as output1:
        for i in range(10):
            expensive_func10(i)
    
    assert np.all(output1 == np.arange(10).astype(str))
    
    with Capturing() as output2:
        for i in range(20):
            expensive_func10(i)
    assert np.all(output2 == np.arange(10, 20).astype(str))
    
    
    
def test_shelve():
    """Test shelving."""
    
    cache1 = Cache(globals())
    cache1.delete_shelve()
    cache1.reset()
    
    @cache1.decorate(save=True)
    def expensive_func(x):
        print(x)
        return x*2
    with Capturing() as output:
        expensive_func(1)
        expensive_func(2)
    assert len(output) == 2
    cache1.reset()
    
    
    print('')
    cache2 = Cache(globals())
    @cache2.decorate(save=True)
    def expensive_func(x):
        print(x)
        return x*2
    
    with Capturing() as output:
        expensive_func(1)
        expensive_func(2)
        expensive_func(3)
    assert len(output) == 1
    # breakpoint()




    
if __name__ == '__main__':
    
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)



    # test_caller()
    # test_decorator()    
    # test_repeated_names()
    # test_arg_cache()
    # test_default_cache_size()
    # test_settings_size()
    # test_settings_disable()
    # test_arguments()
    # test_arguments2()
    # test_reset_cache()
    # test_save_cache()
    # test_cache_import()
    test_shelve()
    # scratch1()

    
        
    