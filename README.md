Globalcache
-----------
Globalcache allows you to store results in iPython or Spyder globals().
This lets you re-run a script and skip the heavy computing if the result 
has already been processed.

Globalcache can also cache function results to disk.

The objective is to speed up development of computationally expensive code. 
Cache the results of code you know to be correct while you iteratively 
debug and develop the rest of your code.


Spyder Requirements
--------------------
In the "Run" preferences, you must sest to **"Run in console's namespace instead of 
an empty one"**. 

Or when Spyder calls `spydercustomize.runfile`, set 

    >>> spydercustomize.runfile(current_namespace = True)

Usage
-----

Create a cache:
    
    >>> from globalcache import Cache
    >>> cache = Cache(globals())
    

Decorate an expensive function:

    >>> @cache.decorate
    >>> def func1(*args, **kwargs):
    >>>     ....
    >>>     return output
    >>> out = func1()
    
    # Note that args & kwargs must be hashable. 


Reset the cache of a function (force delete old values):
    
    >>> @cache.decorate(reset=True)
    >>> def func1(*args, **kwargs):
    >>>    ....


Save cache to disk:
    
    >>> @cache.decorate(save=True)
    >>> def func2(*args, **kwargs):
    >>>     ...
    
    
Clear out cache from globals():

    >>> cache.reset()
    
Delete cache from disk:

    >>> cache.delete_shelve()
    
Set limitations on how many results we can store at a time:

    >>> @cache.decorate(size_limit=5)
    >>> def func2(*args, **kwargs):
    >>>     ...
	
	
	
Store a parameter with an if block:
    
    >>> var1 = cache.var('my-param')
    >>> if var1.not_cached:
    >>>     out = expensive_function()
    >>>     var1.set(out)
    >>> out = var1.get()
	
	
Force disable the globalcache:

	>>> import globalcache
	>>> globalcache.Settings.disable = True