
__author__ = "Andrea Tramacere"

import json
import yaml

import os
import  numpy as np
from astropy.coordinates import Angle

from flask import Flask, jsonify
from flask_restx import Api, Resource,reqparse
from flask.json import JSONEncoder

from antares_data_server import conf_dir,antares_root_data
from oda_api.data_products import ODAAstropyTable

from .analysis import run_antares_analysis

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            print('hi')
            return list(obj)

        return JSONEncoder.default(self, obj)


#template_dir =os.path.abspath(os.path.dirname(__file__))+'/templates'
#static_dir=os.path.abspath(os.path.dirname(__file__))+'/static'

micro_service = Flask("micro_service")
micro_service.json_encoder = CustomJSONEncoder


api= Api(app=micro_service, version='1.0', title='ANTARES back-end API',
    description='API to extract UL for ANTARES Telescope\n Author: Andrea Tramacere',)
ns_conf = api.namespace('api/v1.0/antares', description='data access')


class Configurer(object):
    def __init__(self, cfg_dict):
        self._valid=['port','url','data_dir','out_dir']
        self._validate(cfg_dict)

        for k in cfg_dict.keys():
            setattr(self,k,cfg_dict[k])

        if 'root_wd' not in cfg_dict.keys() or self.root_wd is None:
            self.root_wd=os.path.abspath(os.path.curdir)

    def _validate(self,cfg_dict):
        for k in cfg_dict.keys():
            if k not in self._valid:
                raise RuntimeError('conf key',k,'is not valid')

    @classmethod
    def from_conf_file(cls, conf_file):

        def_conf_file=os.path.join(conf_dir,'config.yml')

        with open(def_conf_file, 'r') as ymlfile:
            cfg_dict=yaml.load(ymlfile,Loader=yaml.FullLoader)

        with open(conf_file, 'r') as ymlfile:

            user_cfg_dict = yaml.load(ymlfile,Loader=yaml.FullLoader)

        for k in user_cfg_dict.keys():
            cfg_dict[k]=user_cfg_dict[k]

        return Configurer(cfg_dict)


class APIError(Exception):

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message

        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        print('API Error Message',message)

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error_message'] = self.message
        return rv

class APP(Exception):
    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message

        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        print('APP Error Message',message)

def angle_conversion(angle):
    try:
        a=Angle(angle)
    except:
        a=Angle(angle,unit='deg')

    return a.to('deg').value

@ns_conf.route('/test-connection')
class TestConnection(Resource):
    @api.doc(responses={200: ''},)
    def get(self):
        config = micro_service.config.get('conf')
        try:
            return jsonify(['connection OK'])
        except Exception as e:
            #print(e)
            raise APIError('NO connection =%s'%repr(e), status_code=500)


@ns_conf.route('/get-ul-table')
class AntaresULTable(Resource):
    @api.doc(responses={200: ''}, params={'ra': 'right ascension',
                                          'dec':'declination',
                                          'roi':'radius of the roi',
                                          'index_min': 'min photon index',
                                          'index_max': 'max photon index',
                                          'job_id':'job_id from disp/fe'})
    def get(self,serialize=True):
        """
        returns the UL  Table to genearate the envelope for a given position RA and DEC and ROI
        """
        api_parser = reqparse.RequestParser()
        api_parser.add_argument('ra', required=True, help="RA", type=str)
        api_parser.add_argument('dec', required=True, help="DEC", type=str)
        api_parser.add_argument('roi', required=True, help="ROI size", type=float)
        api_parser.add_argument('index_min', required=True, help="", type=float,default=1.5)
        api_parser.add_argument('index_max', required=True, help="", type=float,default=3.0)
        api_parser.add_argument('job_id', required=False, help="", type=str, default='unset')
        api_args = api_parser.parse_args()


        try:

            ra = angle_conversion(api_args['ra'])
            dec = angle_conversion(api_args['dec'])
            roi = api_args['roi']
            job_id = api_args['job_id']
            index_min = api_args['index_min']
            index_max = api_args['index_max']

            config = micro_service.config.get('conf')


            out_dir = config.out_dir
            data_dir = config.data_dir
            #print('data_dir',data_dir)
            if data_dir is None:
                data_dir=antares_root_data
            #print('data_dir', data_dir)
            #print('out_dir', out_dir)
            file_name = 'ant_ul_ra%.2f_dec%.2f_roi%.1f_job%s.txt' % (ra, dec, roi, job_id)

            if not os.path.exists(out_dir):
                os.makedirs(out_dir)

            ul_table, table = run_antares_analysis(ra,
                                         dec,
                                         roi,
                                         index_min,
                                         index_max,
                                         data_dir,
                                         out_dir,
                                         file_name)
            ul_file_path = os.path.join(out_dir, "byind_%s" % file_name)
            file_path = os.path.join(out_dir, file_name)

            if serialize is True:
                _o_dict_0 = {}
                _o_dict_0['astropy_table'] = table.encode(use_binary=False)
                _o_dict_0['file_path']=file_path
                _o_dict_1 = {}
                _o_dict_1['astropy_table'] = ul_table.encode(use_binary=False)
                _o_dict_1['file_path']=ul_file_path
                _o_list = json.dumps([_o_dict_0, _o_dict_1])
                _out=jsonify(_o_list)
            else:
                _out=[(table,file_path), (ul_table,ul_file_path)]
        except Exception as e:

            raise APIError('UL table error: %s' % e, status_code=410)

        return _out


def config_micro_service(conf):
    micro_service.config['conf'] = conf
    micro_service.config["JSON_SORT_KEYS"] = False

    print(micro_service.config,micro_service.config['conf'])
    return micro_service

def run_micro_service(conf,debug=False,threaded=False):
    config_micro_service(conf)

    micro_service.run(host=conf.url,port=conf.port,debug=debug,threaded=threaded)



    