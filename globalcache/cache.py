# -*- coding: utf-8 -*-
import inspect
import shelve
import os
from os.path import basename, dirname, join, splitext
from typing import Callable, NewType, TypeVar, Union, Any
from collections import OrderedDict
import logging
import shutil
from functools import cached_property

logger = logging.getLogger(__name__)


DEFAULT_GLOBAL_CACHE_NAME = '__GLOBAL_CACHE__'
DEFAULT_SIZE_LIMIT = 10
DEFAULT_DISABLE = False
DEFAULT_SAVE_DIR = '.globalcache'

# GLOBAL_CACHE_NAME = os.environ.get('GLOBAL_CACHE_NAME', 
#                                    '__GLOBAL_CACHE__')

# DISABLE = os.environ.get('GLOBAL_CACHE_DISABLE', '')
# if DISABLE == '1':
#     DISABLE = True
# else:
#     DISABLE = False

# SIZE_LIMIT = os.environ.get('GLOBAL_CACHE_SIZE_LIMIT', '10')
# SIZE_LIMIT = int(SIZE_LIMIT)
# if SIZE_LIMIT <= 0:
#     SIZE_LIMIT = None


# SAVE_DIR = os.environ.get('GLOBAL_CACHE_SAVE_DIR', '.globalcache')

class Settings:
    """Global settings for globalcache. 
    These will overwrite local settings if set. 
    
    Attributes
    ----------
    global_cache_name : str 
        Name of cache to be inserted into `globals()`
        Set to '' for default. 
    disable : bool
        True to disable global caching. 
    size_limit : int or None
        Maximum size of cache for each cached variable. Set SIZE_LIMIT <= 0
        for unlimited length. 
        Set None for default length.
    """
    global_cache_name = ''
    disable = DEFAULT_DISABLE
    size_limit = None
    save_dir = ''


# class Environ:
#     """Read any environmental variables."""
#     @staticmethod
#     def size_limit():
#         out = os.environ.get('GLOBAL_CACHE_SIZE_LIMIT', DEFAULT_SIZE_LIMIT)
#         return out
    
#     @staticmethod
#     def disable():
#         out = os.environ.get('GLOBAL_CACHE_DISABLE', '0')
#         if out == '1':
#             return True
#         return DEFAULT_DISABLE
    
#     @staticmethod
#     def save_dir():
#         out = os.environ.get('GLOBAL_CACHE_SAVE_DIR', '')
#         if out == '':
#             return DEFAULT_SAVE_DIR
#         else:
#             return out
        
        
def get_size_limit(size_limit: int) -> int:
    """Get size limit. Global limit will overwrite local setting."""
    # out = os.environ.get('GLOBAL_CACHE_SIZE_LIMIT', size_limit)
    if Settings.size_limit is not None:
        return Settings.size_limit
    
    if size_limit is not None:
        return size_limit
    else:
        return DEFAULT_SIZE_LIMIT


def get_disable() -> bool:
    # out = os.environ.get('GLOBAL_CACHE_DISABLE', '0')
    return Settings.disable


def get_save_dir(save_dir: str) -> str:
    """Get save directory. Global save_dir will over-write local preference."""
    # out = os.environ.get('GLOBAL_CACHE_SAVE_DIR', save_dir)
    if Settings.save_dir != '':
        return Settings.save_dir
    if save_dir != '':
        return save_dir
    else:
        return DEFAULT_SAVE_DIR
    
        
    

class CacheError(Exception):
    pass



class LimitDict(OrderedDict):
    """Dictionary with limited size."""
    def __init__(self, *args, _size_limit: int=None, **kwargs):
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
                
CacheValue = TypeVar('CacheValue')
CacheDict = TypeVar('CacheDict', bound=dict[str, LimitDict[str, CacheValue] ])



class Cache:
    """Global cache to cache values in ipython session.
    
    Parameters
    ----------
    g : dict
        Must be set to `globals()`.
    name : str, optional
        Name of dictionary stored in globals(). 
        Defaults to `DEFAULT_GLOBAL_CACHE_NAME`.
    reset : bool, optional
        Force reset of globalcache. The default is False.
        
    """    
    
    cache : CacheDict
    _global_vars : set[str]
    size_limit : int

    def __init__(self,
                 g: dict, 
                 name: str=None, 
                 reset: bool=False,
                 size_limit: int=None,
                 save_dir='',
                 ):
        self.set_globals(g, name, reset, size_limit, save_dir)
    
    def set_globals(
            self, 
            g: dict,
            name: Union[str, None] = None, 
            reset: bool = False,
            size_limit: Union[int, None] = None,
            save_dir: str='',
            ):
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
        
        # if name is None:
        #     name = Settings.GLOBAL_CACHE_NAME
        # if size_limit is None:
        #     size_limit = Settings.SIZE_LIMIT
        # if save_dir == '':
        #     save_dir = Settings.SAVE_DIR

        
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
        self.save_dir = save_dir
        self.function_cache_names  = {}
        self.function_caches = {}
        self._globals = g
        
        return
    
    
    def var(self,
            name: str, 
            args: tuple=(),
            kwargs: dict={}, 
            size_limit=None,
            save: bool = False,
            module: str = '',
            ) -> 'CacheVar':
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
        if size_limit is None:
            size_limit = self.size_limit
            
        return CacheVar(self, name=name, args=args, kwargs=kwargs,
                        size_limit=size_limit, save=save, module=module)
            
        
    
    def decorate(self,
                 fn : Union[None, Callable] = None,
                 size_limit: Union[None, int] = None, 
                 reset: bool = False,
                 save: bool = False,
                 ) -> Callable:
        """Decorate an expensive function to cache the result. 

        Parameters
        ----------
        fn : Callable
            Function to decorate.
            
        size_limit : int, optional
            Max cache size (keyword argument not supported)

        Returns
        -------
        func : Callable 
            Decorated function. Note this function has an additional 
            attribute `fn_cache` to retrieve the FunctionCache object.
        """        
        if size_limit is None:
            size_limit = self.size_limit
        
        if callable(fn):
            return self._sub_decorate(
                fn, 
                size_limit=size_limit,
                reset=False,
                save=False,
                )
        else:
            
            def func(fn):
                return self._sub_decorate(
                    fn, 
                    size_limit=size_limit,
                    reset=reset,
                    save=save,
                    )
        return func
        
                            
    def _sub_decorate(self, fn: Callable, 
                      size_limit: int,
                      reset : bool,
                      save : bool,
                      name: str = '',
                      ):
        
        fn_cache = FunctionCache(self,
                                 fn=fn,
                                 size_limit=size_limit,
                                 save=save, 
                                 name=name
                                 )
        # self._function_caches.append(fn_cache)
        
        key = fn_cache.module + '-' + fn_cache.name
        self.function_caches[key] = fn_cache
        if reset:
            fn_cache.reset()
            
        def func(*args, **kwargs):
            return fn_cache(*args, **kwargs)
        
        
        func.fn_cache = fn_cache
            
        return func
    
            
   
    
    # def decorate_reset(self, fn: Callable) -> Callable:
    #     """Force recalulate the value of the expension function."""
    #     module = inspect.getsourcefile(fn)
    #     name = get_name(fn)
    #     # name = fn.__name__        
        
    #     def func(*args, **kwargs):
    #         logger.debug('Resetting %s', name)
    #         var = CacheVar(self, module, name, args, kwargs, 
    #                        size_limit=self.size_limit)
    #         out = fn(*args, **kwargs)
    #         var.reset()
    #         var.set(out)
    #         return out
    #     return func
    

    def reset(self):
        """Reset the global cache dict."""
        self.cache.clear()
        for fun_cache in self.function_caches.values():
            fun_cache.reset()
        
        
    def delete_shelve(self):
        """Delete persistent shelve file data."""
        dir1  = self.save_dir
        dir1 = get_save_dir(dir1)

        if os.path.exists(dir1):
            shutil.rmtree(dir1)
            
        # Reset to reinitiatlize FunctionCache
        for fn_cache in self.function_caches.values():
            fn_cache._is_first_run = True
        
        
        
    @property
    def module_names(self) -> list[str]:
        """Names of all cached modules."""
        return list(self.cache.keys())
    
    def module_names_short(self) -> list[str]:
        names = [splitext(basename(path))[0] for path in self.module_names]
        out = rename_duplicates(names)
        return out
    
    
    def get_module_short_name(self, name: str):
        """Take module name and return a shortened version."""
        d = dict(zip(self.module_names, self.module_names_short()))
        return d[name]


    
        
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
        
def rename_duplicates(lst: list) -> list:
    """Rename duplicates in a list. From ChatGTP"""
    seen_elements = {}
    renamed_list = []

    for element in lst:
        if element in seen_elements:
            seen_elements[element] += 1
            new_element = f"{element}_{seen_elements[element]}"
        else:
            seen_elements[element] = 1
            new_element = element

        renamed_list.append(new_element)

    return renamed_list


            

class FunctionCache:
    """
    

    Parameters
    ----------
    cache : Cache
        Cache from globalcache.
    fn : Callable
        Function to cache.
    size_limit : int
        Maximum number of values to store.
    save : bool
        Save output to file? True for yes.
    name : str, optional
        Name of function. The default is '' and uses inspect to get the name.
    module : str, optional
        Name of module. The default is '' and uses inspect to get the module..


    Raises
    ------
    CacheError
        Raised if you attempt to define a cache for a function multiple times.

    Attributes
    ----------
    
    shelve_name : str
        Name of file corresponding to shelve file storage.
    fcache : dict
        Cache dictionary for function.
        

    """

    def __init__(self, cache: Cache,
                 fn : Callable,
                 size_limit: int,
                 save: bool,
                 name: str = '',
                 module: str = '',
                 ):

        # Initialize deafault settings
        if module == '':
            module = inspect.getsourcefile(fn)
        if name == '':
            name = get_name(fn)       
        size_limit = get_size_limit(size_limit)
            
        # Get module-level dictionary
        self.module_dict = cache.cache.setdefault(module, {})
        
        # Get argument-value dictionary
        self.fcache = self.module_dict.setdefault(
            name,
            LimitDict(_size_limit=size_limit)
            )
        self.name = name
        self.save = save
        self.size_limit = size_limit
        self.module = module
        self._cache = cache
        self.fn = fn
        self._is_first_run = True
        
        # Read shelve data        
        # module_hash = module.replace('\\','').replace(':','').replace('.','')
        # module_fname = splitext(basename(module))[0]
        # self.shelve_name = f'{module_fname}-{module_hash}'
        self.shelve_name = cache.get_module_short_name(module)
            
        # Track definitions to prevent redefinition.
        function_list = cache.function_cache_names.setdefault(module, [])
        if name in function_list:
            raise CacheError(f'{name} cannot be redefined for module {module}')
        else:
            function_list.append(name)
            
            
            
    def is_cached(self, *args, **kwargs) -> bool:
        """Check whether given arguments for function has cached value."""
        if kwargs is not None:
            kwargs2 = frozenset(kwargs.items())
        else:
            kwargs2 = None
            
        key = (args, kwargs2)
        
        
        if key in self.fcache:
            return True
        if self.save:
            shelve_key = str((self.name, args, kwargs))
            if self.is_shelved(shelve_key):
                return True
            
        return False
        
    
        
    def __call__(self, *args, **kwargs):
        """Call the function with caching."""
        
        # Reun as-is if caching is disabled by environ variable. 
        if get_disable():
            logger.debug('Disable flag detected. Disabling cache.')
            return self.fn(*args, **kwargs)
        
        # Initialize file persistence
        if self._is_first_run:
            self._is_first_run = False
            if self.save:
                logger.debug('Initializing shelve')
                self.shelve_init()
                
            
        if kwargs is not None:
            kwargs2 = frozenset(kwargs.items())
        else:
            kwargs2 = None
            
        key = (args, kwargs2)
        try:
            output = self.fcache[key]
            logger.debug('Successfully retrieved key=%s from fcache', key)
            return output
        
        except KeyError:
            
            if self.save:
                shelve_key = str((self.name, args, kwargs))
                try:
                    output = self.shelve_read(key, shelve_key)
                    logger.debug('Successfully read key=%s from shelve', key)
                except KeyError:
                    logger.debug('key=%s not found in any cache. Running function %s', key, self.fn)
                    output = self.fn(*args, **kwargs)
                    self.shelve_save(shelve_key, output)
            else:
                logger.debug('key=%s not found in any cache. Running function %s', key, self.fn)
                output = self.fn(*args, **kwargs)
            
            self.fcache[key] = output
            return output
                
    
    def shelve_init(self):
        """Initialize shelve file persistence."""
        save_dir = self._cache.save_dir
        save_dir = get_save_dir(save_dir)
        dir1 = save_dir
        
        os.makedirs(dir1, exist_ok=True)
        
    
    @cached_property
    def shelve_path(self) -> str:
        """Get shelve file path."""
        save_dir = self._cache.save_dir
        save_dir = get_save_dir(save_dir)
        dir1 = save_dir
        
        path = join(dir1, self.shelve_name)
        return path
    
    
    def shelve_save(self, shelve_key: str, output: Any):
        """Save cache variable to shelve"""

        with shelve.open(self.shelve_path) as db:
            db[shelve_key] = output
            
            
    def shelve_read(self, key: tuple, shelve_key: str) -> Any:
        """Read from shelve."""
        with shelve.open(self.shelve_path) as db:
            out =  db[shelve_key]
            self.fcache[key] = out
        return out
    
    
    def is_shelved(self, shelve_key: str) -> bool:
        """Check if data has been cached to file."""
        with shelve.open(self.shelve_path) as db:
            return shelve_key in db
    
    def reset(self):
        """Delete globals() cache."""
        self.fcache.clear()
        
    
    
class CacheVar:
    """Cache variables. Usually use Cache.var(...) to create this.
    
    Parameters
    ----------
    cache : Cache
        Cache object.
    name : str
        Name of variable cache.
    args : tuple
        arguments.
    kwargs : dict
        keyword arguments.
    size_limit : int
        Max size limit of cache.
    save : bool
        Save to disk?
    module : str, optional
        Module name. The default is ''.
        
        
    Attributes
    ----------
    key : tuple
        Hashable key used to map arguments to output dictionary
    fn_cache : FunctionCache
        FunctionCache object used to drive calculations
    

    """
    fn_cache : FunctionCache
    
    def __init__(self, cache: Cache,
                 name : str,
                 args : tuple,
                 kwargs: dict,
                 size_limit: int,
                 save: bool,
                 module: str = '',
                 ):

        
        self.cache = cache
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.save = save

        def fn(*args, **kwargs):
            raise CacheError('This dummy function should not ever be called.')


        # if kwargs is not None:
        kwargs2 = frozenset(kwargs.items())
        # else:
        #     kwargs2 = frozenset()
            
        self.key = (args, kwargs2)
        self.fn_cache = FunctionCache(
            cache = cache, 
            fn = fn,
            size_limit = size_limit,
            save = save, name = name, module = module
            )
        
    
    def set(self, output: Any):
        """Set cached variable data."""

        self.fn_cache.fcache[self.key] = output
    
        
    @property
    def is_cached(self) -> bool:    
        """Check whether cached values are found."""
        if get_disable():
            return False
        
        return self.fn_cache.is_cached(*self.args, **self.kwargs)
    
    
    @property
    def not_cached(self) -> bool:
        """Return False if no cached values are found."""
        return not self.is_cached
        
    
    def get(self) -> Any:
        return self.fn_cache.fcache[self.key]

        
        

                 
class CacheVarOLD:
    """Create dictionary structure for cache variable.
    
    Parameters
    ----------
    cache : Cache
        Cache.
    module : str
        Python module name.
    name : str
        Python function name.
    args : tuple
        Python function arguments.
    kwargs : dict
        Python function keyword arguments.
    size_limit : int
        Maximum cache size.
    save : bool, optional
        Save results to file. The default is False.
    
    Attributes
    ----------
    module_dict : dict[str, dict]
        Cache for a Python module
        
    fcache : dict[str, LimitDict]
        Cache for a function in the module.
        
    key : tuple
        Function arguments used for fcache key.
        
    name : str
        Name of function. 
        
        
    """
    
    module_dict : dict[str, dict]
    
    def __init__(self, 
                 cache: Cache, 
                 module: str,
                 name: str, 
                 args: tuple, 
                 kwargs: dict,
                 size_limit: int,
                 save: bool = False,
                 reset: bool = False,
                 ):
        
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
        
        
        module_hash = hash(module)
        module_fname = splitext(basename(module))[0]
        # self.shelve_name = self.
        self.shelve_key = str((name, args, kwargs))
        self.save = save
        
        if reset:
            self.reset()
            
        if save:
            try:
                self.shelve_read()
            except FileNotFoundError:
                logger.debug('No file found in shelve for %s %s %s', module, name, self.key)
            except KeyError:
                logger.debug('No key found in shelve for %s %s %s', module, name, self.key)
            
        
        
    def get(self) -> CacheValue:
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
        if self.save:
            self.shelve_save()
            
        return data
    
    def reset(self):
        """Reset cache."""
        if self.key in self.fcache:
            del self.fcache[self.key]
            
            
    def shelve_save(self):
        """Save cache variable to shelve"""
        dir1 = self._cache.save_dir
        # dir1 = os.path.dirname(path)
        os.makedirs(dir1, exist_ok=True)
        path = join(dir1, self.shelve_name)
        with shelve.open(path,) as db:
            db[self.shelve_key] = self.get()
            
            
    def shelve_read(self):
        """Read from shelve."""
        dir1 = self._cache.save_dir
        path = join(dir1, self.shelve_name)
        with shelve.open(path) as db:
            out =  db[self.shelve_key]
            self.fcache[self.key] = out
        return out
    
        
        
        
    def __bool__(self):
        """Return self.is_cached."""
        
        return self.is_cached
        
