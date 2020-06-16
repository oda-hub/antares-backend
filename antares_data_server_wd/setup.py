
from __future__ import absolute_import, division, print_function

from builtins import (bytes, str, open, super, range,
                      zip, round, input, int, pow, object, map, zip)

__author__ = 'andrea tramacere'




#!/usr/bin/env python

from setuptools import setup, find_packages
import  glob
import  json


f = open("./requirements.txt",'r')
install_req=f.readlines()
f.close()


packs=find_packages()

print ('packs',packs)


with open('antares_data_server/pkg_info.json') as fp:
    _info = json.load(fp)

__version__ = _info['version']

include_package_data=True

scripts_list=glob.glob('./bin/*')
setup(name='antares_data_server',
      version=__version__,
      description='A Python Framework for MAGIC high-level data distribution',
      author='Andrea Tramacere',
      author_email='andrea.tramacere@unige.ch',
      scripts=scripts_list,
      package_data={'antares_data_server': ['config_dir/*','templates/*','static/*']},
      packages=packs,
      include_package_data=True,
      #install_requires=install_req,
      python_requires='>=3.5')



