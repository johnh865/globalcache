# -*- coding: utf-8 -*-
import inspect
import os
from typing import Callable
from collections import OrderedDict
import logging


logger = logging.getLogger(__name__)

GLOBAL_CACHE_NAME = os.environ.get('GLOBAL_CACHE_NAME', 
                                   '__GLOBAL_CACHE__')

DISABLE = os.environ.get('GLOBAL_CACHE_DISABLE', '')
if DISABLE == '1':
    DISABLE = True
else:
    DISABLE = False

SIZE_LIMIT = os.environ.get('GLOBAL_CACHE_SIZE_LIMIT', '10')
SIZE_LIMIT = int(SIZE_LIMIT)
if SIZE_LIMIT <= 0:
    SIZE_LIMIT = None



class Settings:
    """Default settings for globalcache.
    
    Attributes
    ----------
    GLOBAL_CACHE_NAME : str
        Name of cache to be inserted into `globals()`
    DISABLE : bool
        True to disable global caching. 
    SIZE_LIMIT : int
        Maximum size of cache for each cached variable. Set SIZE_LIMIT <= 0
        for unlimited length. 
    """
    GLOBAL_CACHE_NAME = GLOBAL_CACHE_NAME
    DISABLE = DISABLE
    SIZE_LIMIT = SIZE_LIMIT



class LimitDict(OrderedDict):
    """Dictionary with limited size."""
    def __init__(self, *args, _size_limit=None, **kwargs):
        self.size_limit = _size_limit
        super().__init__(*args, **kwargs)
        self._check_size_limit()
    
    
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._check_size_limit()
        
    
    def _check_size_limit(self):
        if self.size_limit is not None:
            while len(self) > self.size_limit:
                self.popitem(last=False)
                

class Cache:
    """Global cache to cache values in ipython session.
    
    Parameters
    ----------
    g : dict
        Must be set to `globals()`.
    name : str, optional
        Name of dictionary stored in globals(). The default is set by
        environment variable 'GLOBAL_CACHE_NAME'.
    reset : bool, optional
        Force reset of globalcache. The default is False.

    """    
    def __init__(self,
                 g: dict, 
                 name: str=None, 
                 reset: bool=False,
                 size_limit=None
                 ):
        self.set_globals(g, name, reset, size_limit)
    
    def set_globals(self, g: dict,
                 name=None, 
                 reset=False,
                 size_limit=None):
        """Use this method to re-set the globals() dict for the cache.
        This is needed to enable the cache from another script. 
        
        
        Example
        -------
        module1.py
        
        >>> from globalcache import Cache
        >>> cache = Cache(globals())
        
        main.py
        
        >>> from module1 import cache
        >>> cache.set_globals(globals())
        
        """
        
        if name is None:
            name = Settings.GLOBAL_CACHE_NAME
        if size_limit is None:
            size_limit = Settings.SIZE_LIMIT

        
        if name in g:
            if reset:
                self.cache = {}
            else:
                self.cache = g[name].cache
        else:
            self.cache = {}
        
        # Make sure to set self into globals()
        g[name] = self        
        
        # Keep track of what is set into self.var(...)
        self._global_vars = set()
        self.size_limit = size_limit
        return
    
    
    def var(self,
            name: str, 
            args: tuple=(),
            kwargs: dict=None, 
            size_limit=None) -> 'CacheVar':
        """Create cached variable. 

        Parameters
        ----------
        name : str
            Name of variable. Must be unique.
        args : tuple, optional
            Hashable arguments for result identification. The default is ().
        kwargs : dict, optional
            Hashable kwargs for result identification. The default is None.
        size_limit : int, optional
            Max size of cached results. The default is None.

        Raises
        ------
        ValueError
            Raised if you repeat a variable name.

        Returns
        -------
        CacheVar
        """
        
        dictname = name
        if name in self._global_vars:
            raise ValueError(f'Var "{name}" cannot be repeated. Use a unique name.')
        self._global_vars.add(name)
        
        if size_limit is None:
            size_limit = self.size_limit
        return CacheVar(self, dictname, name, args, kwargs, size_limit)
    
    
    def decorate(self, fn=None, size_limit=None, reset=False) -> Callable:
        """Decorate an expensive function to cache the result. 

        Parameters
        ----------
        fn : Callable
            Function to decorate.
        size_limit : int, optional
            Max cache size (keyword argument not supported)

        Returns
        -------
        Callable
        """
        if callable(fn):
            return self._sub_decorate(fn, size_limit=self.size_limit)
        
        elif reset:
            return self.decorate_reset
 
        
        elif size_limit is not None:
            def func(fn):
                return self._sub_decorate(fn, size_limit=size_limit)
            return func
        
        else:
            raise ValueError('Wrong keyword argument set')
        
                            
    def _sub_decorate(self, fn: Callable, size_limit: int):
        module = inspect.getsourcefile(fn)
        name = get_name(fn)
        # name = fn.__name__
        
        # print(module)
        # print(name)


        def func(*args, **kwargs):
            var = CacheVar(self, module, name, args, kwargs, 
                           size_limit=size_limit)
            if var.not_cached:
                out = fn(*args, **kwargs)
                var.set(out)
            else:
                out = var.get()
            return out
        return func
    
    
    def decorate_reset(self, fn: Callable) -> Callable:
        """Force recalulate the value of the expension function."""
        module = inspect.getsourcefile(fn)
        name = get_name(fn)
        # name = fn.__name__        
        
        def func(*args, **kwargs):
            logger.debug('Resetting %s', name)
            var = CacheVar(self, module, name, args, kwargs, 
                           size_limit=self.size_limit)
            out = fn(*args, **kwargs)
            var.reset()
            var.set(out)
            return out
        return func
    

    def reset(self):
        self.cache = {}
        
        
def get_name(fn : Callable) -> str:
    """Create a name for a callable function."""
    name = fn.__name__
    while True:
        try:
            parent = fn.__self__
            fn = parent.__class__
            parent_name = fn.__name__
            name = parent_name + '.' + name
        except AttributeError:
            break
    return name
        
            
        

class CacheVar:
    """Create dictionary structure for cache variable."""
    def __init__(self, 
                 cache: Cache, 
                 module: str,
                 name: str, 
                 args: tuple, 
                 kwargs: dict,
                 size_limit: int):
        
        # print('CacheVar:', module, name)
        # Get module-level dictionary
        self.module_dict = cache.cache.setdefault(module, {})
        
        # Get argument-value dictionary
        self.fcache = self.module_dict.setdefault(
            name,
            LimitDict(_size_limit=size_limit)
            )
        
        if kwargs is not None:
            kwargs = frozenset(kwargs.items())
        
        self.key = (args, kwargs)
        self.name = name
        self._cache = cache
        
        
        
    def get(self):
        """Retrieve cached value if it exists.
        
        Raises
        ------
        ValueError
            Raised if cache has not yet been set.
        """
        key = self.key
        try:
            logger.debug('Retrieving %s %s from cache', self.name, key)
            return self.fcache[key]
        except KeyError:
            raise ValueError('Variable not yet set.')
            
            
    @property
    def is_cached(self) -> bool:
        """Check whether a value has been cached."""
        if Settings.DISABLE:
            return False
        # breakpoint()
        return self.key in self.fcache
    
    
    @property
    def not_cached(self) -> bool:
        """Check that a value is not cached."""
        if Settings.DISABLE:
            return True
        # breakpoint()
        return self.key not in self.fcache
    
    
    def set(self, data):
        """Set data into cache.
        
        Returns
        -------
        data : 
            Return input argument.
        """
        logger.debug('Saving %s %s into cache', self.name, self.key)
        self.fcache[self.key] = data
        return data
    
    def reset(self):
        if self.key in self.fcache:
            del self.fcache[self.key]
        
        
    def __bool__(self):
        """Return self.is_cached."""
        
        return self.is_cached
        
