from __future__ import absolute_import, division, print_function

from builtins import (open, str, range,
                      object)

from astropy.table import Table
import json
import pickle
import base64

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def get_targets_dic(targets_dic):
    target_names = [k for k in targets_dic if 'Tpname' in k]
    names_dict = {}
    target_names.sort()
    for ID, n in enumerate(target_names):
        l = [targets_dic[n]]
        if n.replace('pname', 'aname') in targets_dic:
            alias = targets_dic[n.replace('pname', 'aname')]
            if alias is not None:
                l.extend(targets_dic[n.replace('pname', 'aname')].split(';'))
        names_dict['src_%02d' % ID] = l

    return names_dict






class ANTARESTable(object):

    def __init__(self,table_object,name='astropy table', meta_data={}):
        self.name=name
        self.meta_data=meta_data
        self.table=table_object


    @classmethod
    def from_file(cls,file_path,format,name,delimiter=' '):
        table=Table.read(file_path, format=format,delimiter=delimiter)

        meta=None

        if hasattr(table,'meta'):
            meta=table.meta

        return cls(table,name,meta_data=meta)


    def encode(self,use_binary=False,to_json = False):

        _o_dict = {}
        _o_dict['binary']=None
        _o_dict['ascii']=None

        if use_binary is True:
            _binarys = base64.b64encode(pickle.dumps(self.table, protocol=2)).decode('utf-8')
            _o_dict['binary'] = _binarys
        else:
            fh=StringIO()
            self.table.write(fh, format='ascii.ecsv')
            _text = fh.getvalue()
            fh.close()
            _o_dict['ascii'] = _text

        _o_dict['name']=self.name
        _o_dict['meta_data']=json.dumps(self.meta_data)

        if to_json == True:
            _o_dict=json.dumps(_o_dict)
        return   _o_dict

    @classmethod
    def decode(cls,_o_dict,use_binary=False):

        encoded_name = _o_dict['name']
        encoded_meta_data = _o_dict['meta_data']
        if use_binary is True:
            t_rec = base64.b64decode(_o_dict['binary'])
            try:
                t_rec = pickle.loads(t_rec)
            except:
                t_rec= pickle.loads(t_rec,encoding='latin')

        else:
            t_rec = ascii.read(_o_dict['ascii'])

        return cls(t_rec,name=encoded_name,meta_data=encoded_meta_data)



