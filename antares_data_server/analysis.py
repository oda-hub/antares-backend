import numpy as np
import subprocess as sp
from oda_api.data_products import ODAAstropyTable
from astropy.units import Unit
from antares_data_server import antares_exc
from astropy.table import QTable
import os

def pl_function(energy, pl_index, norm):
    return np.power(energy, -pl_index) * norm

def run_antares_analysis(ra,
                         dec,
                         roi,
                         index_min,
                         index_max,
                         data_dir,
                         out_dir,
                         file_name):

    
    out_size = 100
    byind_fn = "byind_%s" % file_name
    exec_cmd='%s %f %f %f %f %f %s %s %s'%(antares_exc, 
                                           dec, 
                                           ra, 
                                           index_min, 
                                           index_max, 
                                           roi, 
                                           data_dir, 
                                           out_dir, 
                                           byind_fn)
    print('cmd',exec_cmd)
    res=sp.check_call(exec_cmd, shell=True)
    print('done', res)
    
    ul_table_t = ODAAstropyTable.from_file(file_path = os.path.join(out_dir, byind_fn), 
                                           format = 'ascii.ecsv',
                                           delimiter = ' ')
    ul_table = ul_table_t.table
    meta_data = ul_table_t.meta_data

    ul_sed = np.zeros(out_size)
    e_range = np.logspace(-1, 6, out_size)

    for ID, energy in enumerate(e_range):
        ul_sed[ID] = np.max(pl_function(energy, 
                                        ul_table['Index'], 
                                        ul_table['1GeV_norm']))

    ul_sed = ul_sed * ul_table['1GeV_norm'].unit
    e_range = e_range * Unit('GeV')
    ul_sed = ul_sed * e_range * e_range
    
    tdat = QTable([e_range, ul_sed], names = ['E', 'flux_UL * E^2'] )
    
    out_table = ODAAstropyTable(tdat, name='Spectra Upper Limit', meta_data=meta_data)
    
    out_table.write(os.path.join(out_dir, file_name), format='ascii.ecsv')
    
    return ul_table_t, out_table