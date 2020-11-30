
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


def compile_and_install_software():
    """Used the subprocess module to compile/install the C software."""
    src_path = './some_c_package/'

    # compile the software
    cmd = "./configure CFLAGS='-03 -w -fPIC'"
    venv = get_virtualenv_path()
    if venv:
        cmd += ' --prefix=' + os.path.abspath(venv)
    subprocess.check_call(cmd, cwd=src_path, shell=True)

    # install the software (into the virtualenv bin dir if present)
    subprocess.check_call('make install', cwd=src_path, shell=True)


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



