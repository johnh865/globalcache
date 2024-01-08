"""
Globalcache
-----------
Globalcache allows you to store results in IPython or Spyder globals().
This lets you re-run a script and skip the heavy computing if the result 
has already been processed, when you rerun your script. 

The purpose of this is for rapid development for scientific and datascience 
purposes. 


Spyder Requirements
--------------------
Globalcache only works with the option "Run in console's namespace instead of 
an empty one". Or when Spyder calls `spydercustomize.runfile`, set 

>>> spydercustomize.runfile(current_namespace = True)

Usage
-----

Create a cache with:
    
    >>> from globalcache import Cache
    >>> cache = Cache(globals())
    
Decorate an expensive function:

    >>> @cache.decorate
    >>> def func1(*args, **kwargs):
    >>>     ....
    >>>     return output
    >>> out = func1()
    
    
    Note that args & kwargs must be hashable. 


Reset the cache of a function (force delete old values):
    
    >>> @cache.decorate_reset
    >>> def func1(*args, **kwargs):
    >>>    ...


Store a parameter with an if block:
    
    >>> var1 = cache.var('my-param')
    >>> if var1.not_cached:
    >>>     out = expensive_function()
    >>>     var1.set(out)
    >>> out = var1.get()
    


Use settings to modify global configuration:
    
    >>> from globalcache import Settings
    
    Disable the cache
    
        >>> Settings.DISABLE = True
    
    Set default cache size. Set to None for unlimited size.
    
        >>> Settings.SIZE_LIMIT = None
        >>> Settings.SIZE_LIMIT = 100
        
        
    Rename the default dictionary name
        
        >>> Settings.GLOBAL_CACHE_NAME = 'my-new-name'

"""





from globalcache.cache import Cache, Settings