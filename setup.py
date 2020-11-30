
from __future__ import absolute_import, division, print_function

from builtins import (bytes, str, open, super, range,
                      zip, round, input, int, pow, object, map, zip)

__author__ = 'andrea tramacere'




#!/usr/bin/env python

from setuptools import setup, find_packages
import  glob
import  json
import subprocess
import  shutil
from setuptools.command.install import install


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
    src_path = './antares_src'

    # compile the software
    cmd = "g++ -std=c++11 multiMessenger.cc -o multiMessenger `root-config --cflags --glibs`"

    subprocess.check_call(cmd, cwd=src_path, shell=True)

    src_path='./'
    subprocess.check_call('cp antares_src/multiMessenger antares_data_server/antares_bin', cwd=src_path, shell=True)

class CustomInstall(install):
    """Custom handler for the 'install' command."""
    def run(self):
        compile_and_install_software()
        super().run()

class CustomClean(install):
    def run(self):



        try:
            shutil.rmtree('dist')
        except:
            pass
        try:
            shutil.rmtree('build')
        except:
            pass
        try:
            shutil.rmtree(glob.glob('*.egg-info')[0])
        except:
            pass


custom_cmdclass = {'install': CustomInstall,
                   'clean':CustomClean}

setup(name='antares_data_server',
      version=__version__,
      description='A Python Framework for MAGIC high-level data distribution',
      author='Andrea Tramacere',
      author_email='andrea.tramacere@unige.ch',
      scripts=scripts_list,
      package_data={'antares_data_server': ['config_dir/*','templates/*','static/*','antares_data/*','antares_bin/*']},
      packages=packs,
      include_package_data=True,
      cmdclass=custom_cmdclass,
      python_requires='>=3.5')


