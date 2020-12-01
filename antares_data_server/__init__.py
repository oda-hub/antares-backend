
import pkgutil
import os
import json

__author__ = "Andrea Tramacere"



pkg_dir = os.path.abspath(os.path.dirname(__file__))
pkg_name = os.path.basename(pkg_dir)
__all__=[]
for importer, modname, ispkg in pkgutil.walk_packages(path=[pkg_dir],
                                                      prefix=pkg_name+'.',
                                                      onerror=lambda x: None):

    if ispkg == True:
        __all__.append(modname)
    else:
        pass


with open(os.path.dirname(__file__) + '/pkg_info.json') as fp:
    _info = json.load(fp)

__version__=_info['version']

conf_dir=os.path.dirname(__file__)+'/config_dir'
antares_exc=os.path.dirname(__file__)+'/antares_bin/multiMessenger'
antares_root_data=os.path.dirname(__file__)+'/antares_data'