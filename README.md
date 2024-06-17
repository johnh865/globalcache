Globalcache
===========

Globalcache allows you to store results in iPython, Jupyter, or Spyder.
This lets you re-run a script and skip heavy computing if the result 
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

To initialize the cache, you must input globals() into the Cache. 
    
    >>> from globalcache import Cache
    >>> gcache = Cache(globals())
    

Use the cache to decorate an expensive function and skip the calculation in subsequent runs.


    >>> @gcache.decorate
    >>> def func1(*args, **kwargs):
    >>>     ....
    >>>     return output
    >>> out = func1()
    
*Note: args & kwargs must be hashable.* 




Reset the cache of a function (force delete old values):
    
    >>> @gcache.decorate(reset=True)
    >>> def func1(*args, **kwargs):
    >>>    ....

Clear out cache from globals():

    >>> gcache.reset()


Set limitations on how many results we can store at a time:

    >>> @gcache.decorate(size_limit=5)
    >>> def func2(*args, **kwargs):
    >>>     ...

Saving to disk
---------------


`globalcache` can shelve results to the disk using `decorate`. 
To save the cache to disk, use:
    
    >>> @gcache.decorate(save=True)
    >>> def func2(*args, **kwargs):
    >>>     ...
    
    
Delete the cache files from disk:

    >>> gcache.delete_shelve()
    


By default, results are saved in the current working directory in a folder
called `.globalcache/`. The default can be changed using:
    
    >>> gcache.init(globals(), save_dir='/p/folder1/path_to_new_directory')
    
    
Caching an if-block
--------------------

globalcache can cache a variable and skip an expensive block of code. 
	
Store a parameter with an if block:
    
    >>> var1 = gcache.var('my-param')
    >>> if var1.not_cached:
    >>>     out = expensive_function()
    >>>     var1.set(out)
    >>> out = var1.get()

Results can be cached dependent on the change of other variables:
    
    >>> var2 = gcache.var('param2', args=(args1, args2),
    >>>                   kwargs=dict2, save=False, size_limit=None)
    >>> if var2.not_cached:
    >>>     out = expensive_function()
    >>>     var2.set(out)
    >>> out = var2.get()
    

Disabling the globalcache
-------------------------

Force disable the globalcache:

    >>> import globalcache
    >>> globalcache.Settings.disable = True
    
    
    
Dealing with Unhashable Arguments
---------------------------------
If your function relies on unhashable arguments, there are various
strategies. For example, you can associate unhashable
arguments with hashable parameters. For example:

    >>> dict1 = {'a': [1,2,3],
    >>>          'b': [3,4,5],
    >>>         }
    >>> @cache.decorate
    >>> def func2(key):
    >>>     args = dict1[key]
    >>>     return func1(args) 
    
Or you can use an if-block cache. 

Caching a class method
----------------------
In order to cache a class method, we must make sure the base class has 
implemented `__repr__` special method. For example to 
cache a method `my_method`:

    >>> class MyClass1:
    >>>    def __init__(self, ...):
    >>>       ...
    >>>
    >>>    def __repr__(self):
    >>>       ...
    >>>
    >>>    @cache.decorate
    >>>    def my_method(self, args):
    >>>       ...


