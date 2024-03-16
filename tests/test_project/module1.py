from globalcache import gcache

gcache.init(globals())

@gcache.decorate
def testfun1(x):
    print('testfun1')
    return x**2