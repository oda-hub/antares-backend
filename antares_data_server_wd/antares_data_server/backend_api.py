from flask import Flask, jsonify, abort,request,render_template,Response,make_response
from flask_restplus import Api, Resource,reqparse
from flask.json import JSONEncoder
from .data_tools import ANTARESTable
from antares_data_server import conf_dir
from .plot_tools import ScatterPlot

from astropy.coordinates import Angle
from astropy.units import Unit

import json
import yaml
import pickle
import glob
import os
import  numpy as np

import subprocess as sp

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            print('hi')
            return list(obj)

        return JSONEncoder.default(self, obj)


template_dir =os.path.abspath(os.path.dirname(__file__))+'/templates'
static_dir=os.path.abspath(os.path.dirname(__file__))+'/static'

micro_service = Flask("micro_service",template_folder=template_dir,static_folder=static_dir)
micro_service.json_encoder = CustomJSONEncoder


api= Api(app=micro_service, version='1.0', title='ANTARES back-end API',
    description='API to extract UL for ANTARES Telescope\n Author: Andrea Tramacere',)
ns_conf = api.namespace('api/v1.0/antares', description='data access')




def output_html(data, code, headers=None):
    resp = Response(data, mimetype='text/html', headers=headers)
    resp.status_code = code
    return resp





class Configurer(object):
    def __init__(self, cfg_dict):
        self._valid=['port','url','antares_env_dir','data_dir','out_dir','bin_dir','root_wd','mm_exec']
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


class APIerror(Exception):

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



@micro_service.errorhandler(APP)
def handle_app_error(error):
    return 'bad request! %s'%error.message, 400

@micro_service.route('/index')
def index():
    return render_template("index.html")



@micro_service.route('/get-ul-table',methods=['GET', 'POST'])
def get_ul_table():
    p_dict = get_pars()
    print('->',p_dict)
    try:
        c=AntaresULTable()
        res=c.get(serialize=True)
        return res

    except Exception as e:
        print(e)
        raise APP('table file is empty/corrupted or missing: %s' % e, status_code=410)


@micro_service.route('/plot-ul-envelope',methods=['GET', 'POST'])
def plot_target():
    script = None
    div = None
    p_dict = get_pars()
    print('-> pars', p_dict)
    try:
        c=AntaresULTable()
        table,file_path=c.get(serialize=False)
        print('-->,',table,file_path)
        c=APIPlotUL()
        print('-->,', table, file_path)
        script, div = c.get(render=False,file_path=file_path)
        resp = make_response('{"test": "ok"}')
        resp.headers['Content-Type'] = "text/html"

        print('-->,', table, file_path)
        return Response((script, div), content_type='text/html')

    except Exception as e:
        print(e)
        raise APP('Problem with  APIPlotUL: %s' % e, status_code=410)



def get_pars():
    p_dict=None
    if request.method == 'POST':
        p_dict= request.form

    if request.method == 'GET':
        p_dict = request.args.to_dict()

    return p_dict


def get_file_path(file_name,config=None):
    if config is None:
        config = micro_service.config.get('conf')

    antares_env_dir = config.antares_env_dir
    root_wd = config.root_wd
    out_dir = config.out_dir
    file_path = os.path.join(root_wd, antares_env_dir,out_dir,file_name)

    return file_path


def angle_conversion(angle):
    try:
        a=Angle(angle)
    except:
        a=Angle(angle,unit='deg')

    return a.to('deg').value



@ns_conf.route('/get-ul-table')
class AntaresULTable(Resource):
    @api.doc(responses={410: ''}, params={'ra': 'right ascension',
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
        api_parser.add_argument('job_id', required=False, help="ROI size", type=str, default='test')
        api_args = api_parser.parse_args()


        try:

            ra = angle_conversion(api_args['ra'])
            dec = angle_conversion(api_args['dec'])
            roi = api_args['roi']
            job_id = api_args['job_id']
            index_min = api_args['index_min']
            index_max = api_args['index_max']

            config = micro_service.config.get('conf')

            antares_env_dir=config.antares_env_dir
            out_dir = config.out_dir
            mm_exec = config.mm_exec
            root_wd = config.root_wd
            bin_dir=config.bin_dir

            file_name = 'ul_file_%s_ra_%f2.2_dec_%f2.2.txt' % (job_id, ra, dec)
            run_antares_analysis(ra,
                                 dec,
                                 roi,
                                 index_min,
                                 index_max,
                                 file_name,
                                 antares_env_dir,
                                 bin_dir,
                                 root_wd=root_wd,
                                 mm_exec=mm_exec,
                                 out_dir=out_dir)


            file_path = get_file_path(file_name,config=config)

            table = ANTARESTable.from_file(file_path=file_path, format='ascii', name='ANTARES TABLE')

            if serialize is True:

                _o_dict = {}
                _o_dict['astropy_table'] = table.encode(use_binary=False)
                _o_dict['file_path']=file_path
                _o_dict = json.dumps(_o_dict)
                _out=jsonify(_o_dict)
            else:
                _out=table,file_path
        except Exception as e:

            raise APIerror('UL table error: %s' % e, status_code=410)

        return _out


def pl_fuction(energy, pl_index, norm):
    return np.power(energy, -pl_index) *  norm




@ns_conf.route('/plot-ul-envelope')
class APIPlotUL(Resource):
    @api.doc(responses={410: 'error for UL computation'}, params={'file_path': 'table file path'})
    def get(self,render=True,file_path=None):
        """
        returns the plot for a SED table
        """
        api_parser = reqparse.RequestParser()
        if file_path is None:
            api_parser.add_argument('file_path', required=True, help="the name of the file", type=str)
            api_args = api_parser.parse_args()
            file_path = api_args['table_file']
        else:
            pass

        print('->',file_path)
        try:
            size=100

            ul_table = ANTARESTable.from_file(file_path=file_path, format='ascii', name='ANTARES TABLE', delimiter=' ').table

            ul_sed = np.zeros(size)
            e_range = np.logspace(-1, 6, size)

            for ID, energy in enumerate(e_range):
                ul_sed[ID] = np.max(pl_fuction(energy, ul_table['Index'], ul_table['1GeV_norm']))

            ul_sed =ul_sed*ul_table['1GeV_norm'].unit
            e_range= e_range*Unit('GeV')
            ul_sed= ul_sed * e_range  *e_range
            sp1 = ScatterPlot(w=600, h=400, x_label=str(e_range.unit), y_label=str(ul_sed.unit),
                              y_axis_type='log', x_axis_type='log',title='UL')



            sp1.add_errorbar(e_range, ul_sed)

            script, div = sp1.get_html_draw()
            print('-> s,d',script,div)
            if render is True:
                return output_html(render_template("plot.html", script=script, div=div), 200)
            else:
                return script, div

        except Exception as e:
            #print('qui',e)
            raise APIerror('problem im producing UL plot: %s'%e, status_code=410)


def run_micro_service(conf,debug=False,threaded=False):

    micro_service.config['conf'] = conf
    micro_service.config["JSON_SORT_KEYS"] = False

    print(micro_service.config,micro_service.config['conf'])


    micro_service.run(host=conf.url,port=conf.port,debug=debug,threaded=threaded)


def run_antares_analysis(ra,
                         dec,
                         roi,
                         index_min,
                         index_max,
                         file_name,
                         antares_env_dir,
                         bin_dir,
                         root_wd='/workdir',
                         mm_exec='multiMessenger',
                         out_dir='antares_output'):

    root_env=os.path.join(root_wd,antares_env_dir)

    path_mm_exec=os.path.join(root_wd,bin_dir,mm_exec)
    print('-> path_mm_exec', path_mm_exec)

    exec_list=[path_mm_exec, dec, ra, index_min, index_max, roi, root_wd, out_dir, file_name]
    print('cmd',exec_list)

    c = sp.run(exec_list, check=True, stderr=sp.STDOUT, stdout=sp.PIPE)
    print('done:')
    print(c.stdout)