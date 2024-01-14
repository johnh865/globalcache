Globalcache
-----------
Globalcache allows you to store results in iPython, Jupyter, or Spyder.
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
    
To initialize the cache, you must input the module globals() into the Cache. 
Cache(globals()) will create a dictionary in globals() to store the cache. 

Use the cache to decorate an expensive function and skip the calculation in subsequent runs.


    >>> @cache.decorate
    >>> def func1(*args, **kwargs):
    >>>     ....
    >>>     return output
    >>> out = func1()
    
*Note: args & kwargs must be hashable.*


Reset the cache of a function (force delete old values):
    
    >>> @cache.decorate(reset=True)
    >>> def func1(*args, **kwargs):
    >>>    ....

Clear out cache from globals():

    >>> cache.reset()
	

Set limitations on how many results we can store at a time:

    >>> @cache.decorate(size_limit=5)
    >>> def func2(*args, **kwargs):
    >>>     ...

Saving to disk
==============

`globalcache` can shelve results to the disk using `decorate`. 
To save the cache to disk, use:
    
    >>> @cache.decorate(save=True)
    >>> def func2(*args, **kwargs):
    >>>     ...
    
    
Delete the cache files from disk:

    >>> cache.delete_shelve()
    


By default, results are saved in the current working directory in a folder called .globalcache/
The default can be changed using:
	
	>>> cache = Cache(globals(), save_dir='/p/folder1/path_to_new_directory')
	

Caching an if-block
===================

globalcache can cache a variable and skip an expensive block of code. 
	
Store a parameter with an if block:
    
    >>> var1 = cache.var('my-param')
    >>> if var1.not_cached:
    >>>     out = expensive_function()
    >>>     var1.set(out)
    >>> out = var1.get()
	
Results can be cached dependent on the change of other variables:

	>>> var2 = cache.var('param2', args=(args1, args2), kwargs=dict2, save=False, size_limit=None)
	>>> if var2.not_cached:
	>>> 	out = expensive_function()
	>>>		var2.set(out)
	>>> out = var2.get()
	

Disabling the globalcache
=========================
Force disable the globalcache:

	>>> import globalcache
	>>> globalcache.Settings.disable = True
	
	
Using imported modules
======================
Each Python module will have its own global namespace. If you wish to import a 
module that uses globalcache, you must re-initialize globals() to the __main__ script.

For example:

	# Let's import a cachced function.
	# We also need to import gcache (which is a `Cache` object) from our module.
	>>> from module1 import expensive_func, gcache 
	>>> gcache.set_globals(globals())
	