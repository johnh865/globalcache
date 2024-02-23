# -*- coding: utf-8 -*-

from setuptools import setup, find_packages



setup(
      name='globalcache',
      # version='0.1',   # May 14, 2021 update
       # version='0.1.1',   # Jan 7, 2024  update
       # version='0.1.2',   # Jan 8, 2024  update
       # version='0.1.4',   # Jan 13, 2024  update
       # version='0.1.5',   # Jan 13, 2024  update
        # version='0.1.6',   # Feb 15, 2024  update
        version='0.2.0',   # Feb 22, 2024  update
      packages=find_packages(
          include=["globalcache*"]
          ),
      zip_safe=False,
      )