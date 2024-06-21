# -*- coding: utf-8 -*-
from globalcache.cache import print_status


from tests.example_project import module1, module2
from tests import example_import

module1.gcache.init(globals())
module2.gcache.init(globals())
example_import.gcache.init(globals())


for ii in range(10):
    module1.testfun1(ii)


class2 = module2.Class2(1, 2)
for x in range(10):
    class2.power(x)

print_status()