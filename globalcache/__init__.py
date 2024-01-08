"""
Globalcache
-----------
Globalcache allows you to store results in IPython or Spyder globals().
This lets you re-run a script and skip the heavy computing if the result 
has already been processed, when you rerun your script. 


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



Store a parameter with an if block:
    
    >>> var1 = cache.var('my-param')
    >>> if var1.not_cached:
    >>>     out = expensive_function()
    >>>     var1.set(out)
    >>> out = var1.get()
    


Reset the cache of a function (force delete old values):
    
    >>> @cache.decorate(reset=True)
    >>> def func1(*args, **kwargs):
    >>>    ....

"""





from globalcache.cache import Cache, Settings, CacheError