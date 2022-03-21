#!/usr/bin/env python

import argparse
from openkm3.store import KM3Store
from antares_data_server.backend_api import Configurer
import os
import pandas as pd
import shutil

class ConfigError(Exception):
    pass

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-conf_file', type=str, default=None)
    args = parser.parse_args()
    conf_file = args.conf_file

    conf = Configurer.from_conf_file(conf_file)

    if conf.data_dir:
        os.makedirs(conf.data_dir, exist_ok=True)
    else:
        print('Data directory is not set. Using packaged-in data')
        return 

    if os.environ.get('ANTARES_NO_POPULATE'):
        if (os.path.isfile(os.path.join(conf.data_dir, 'ANTARES.data')) and 
            os.path.isfile(os.path.join(conf.data_dir, 'acc.txt')) and 
            os.path.isfile(os.path.join(conf.data_dir, 'background.txt')) 
           ) or (
            os.path.islink(os.path.join(conf.data_dir, 'ANTARES.data')) and 
            os.path.islink(os.path.join(conf.data_dir, 'acc.txt')) and 
            os.path.islink(os.path.join(conf.data_dir, 'background.txt'))
           ): 
           print('ANTARES data present in ' + conf.data_dir)
           return
        else:
            raise ConfigError('ANTARES_NO_POPULATE environment variable is set, \
                but there is no data in ' + conf.data_dir)

    store = KM3Store()
    interpolation = store.get("ana20_01_bkg")
            
    lookup = store.get('ana20_01_acc')
    acc_df = pd.DataFrame.from_dict(lookup.data)
            
    data = store.get('ana20_01_vo')
    data_df = data.get_dataframe()

    with open(os.path.join(conf.data_dir, 
                            'background.txt'), 'w') as fd:
            print(*interpolation.data, sep=' ', file=fd)
    with open(os.path.join(conf.data_dir, 
                            'acc.txt'), 'w') as fd:
            acc_df.to_csv(fd, sep=' ', index=False, header=False)
    with open(os.path.join(conf.data_dir, 
                            'ANTARES.data'), 'w') as fd:
            data_df.to_csv(fd, columns=['ra', 'decl', 'nhit', 'beta', 'mjd'], 
                        sep='\t', index=False, header=False)

if __name__ == '__main__':
    main()
