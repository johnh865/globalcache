# -*- coding: utf-8 -*-



import logging

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

from globalcache import gcache

gcache.init(globals())

from tests.test_project.module1 import testfun1


out = testfun1(12)
out = testfun1(12)
out = testfun1(12)
out = testfun1(13)