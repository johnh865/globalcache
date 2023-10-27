# -*- coding: utf-8 -*-

import sys
from io import StringIO 
from globalcache import Cache, Settings
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
    if not cvar:
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
    except ValueError:
        print('Good')
    else:
        assert False
        
        
def test_arg_cache():
    """Make sure cache doesn't exceed limit."""
    c = Cache(globals(), reset=True)
    size = 5
    for ii in range(10):
        c = Cache(globals(), reset=False, size_limit=size)
        
        cvar = c.var('a', args=(ii))
        cvar.set(ii)
        
        alen = len(c.cache['a'])
        assert alen <= size
        assert alen == min(ii+1, size)        
    return


def test_default_cache_size():
    
    c = Cache(globals(), reset=True)
    size = Settings.SIZE_LIMIT
    
    for ii in range(10):
        c = Cache(globals(), reset=False)
        
        cvar = c.var('a', args=(ii))
        cvar.set(ii)
        
        alen = len(c.cache['a'])
        assert alen <= size
        assert alen == min(ii+1, size)        
    return    
    
    
def test_settings_size():
    """Test that SIZE_LIMIT actually sets the global size limit."""
    Settings.SIZE_LIMIT = 50
    c = Cache(globals(), reset=True)
    
    
    for ii in range(100):
        c = Cache(globals(), reset=False)
        cvar = c.var('a', args=(ii))
        cvar.set(ii)
                
        alen = len(c.cache['a'])
        assert alen == min(ii+1, Settings.SIZE_LIMIT)        
        
    return


def test_settings_disable():
    """Test to make sure DISABLE actually disables cache."""
    Settings.DISABLE = True
    
    with Capturing() as output1:
        caller1()
        
    with Capturing() as output2:
        caller1()
        
    assert len(output1) == 12
    assert len(output2) == 12
    return
    

def test_arguments():
    c = Cache(globals(), reset=True)
    
    decorator = c.decorate(size_limit=1000)
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
    # breakpoint()
    assert output2[0] == 'c'
    assert out1 == 'aa'
    assert out2 == 'bb'
    assert out3 == 'cc'
    

    # assert output2[0] == ''
    # assert output2[1] == ''
    

if __name__ == '__main__':
    # test_caller()
    # test_decorator()    
    # test_repeated_names()
    # test_arg_cache()
    # test_default_cache_size()
    # test_settings_size()
    # test_settings_disable()
    # logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    test_arguments()
    
        
    