# DARE-API backend

# Native python imports
import sys
import yaml
import json
import ast
import requests

# Backend utils
import backend_utils as butils
# FLASK
from flask import Flask, request, make_response
from flask import render_template, redirect, url_for

app = Flask(__name__)

# Get namespace from yaml
r = requests.get('https://gitlab.com/project-dare/dare-api/raw/master/k8s/nginx-api-dp.yaml')
name_space = yaml.safe_load(r.text)['metadata']['namespace']
# Current pod running flask api
host_pod = butils.init_from_yaml(name_space)

# D4P OPENMPI
_d4p = {}
_d4p['jobname'] = 'd4p-openmpi'
_d4p['mountname'] = host_pod.spec.containers[0].volume_mounts[0].name
_d4p['mountpath'] = host_pod.spec.containers[0].volume_mounts[0].mount_path
_d4p['volname'] = host_pod.spec.volumes[0].name
_d4p['fsname'] = host_pod.spec.volumes[0].flex_volume.options['fsName']
_code = _d4p['mountpath'] + host_pod.spec.volumes[0].flex_volume.options['path'].split('/')[1] + '/code.py'
# SPECFEM
_specfem = {}
_specfem['specname'] = 'd4p-specfem'
_specfem['specvolname'] = host_pod.spec.containers[0].volume_mounts[1].name
_specfem['spec_mountpath'] = host_pod.spec.containers[0].volume_mounts[1].mount_path
_specfem['fsname'] = host_pod.spec.volumes[0].flex_volume.options['fsName']

# Returns PE Impl code and mpi cwl specification

@app.route('/d4p-mpi-spec', methods=['POST'])
def mpi_spec():
    # Load request data
    _data = request.data.decode("utf-8")
    _data = _data.replace('\\"', '"')[1:-1]
    _data = _data.replace('"', '\'')
    data = ast.literal_eval(_data)
    _args = data['d4p_args']
    # Peimpl
    code = butils.findPEimpl(data)
    # MPI spec
    spec = yaml.dump(butils.mpi_input(_code, **_args))
    return json.dumps({'code': code, 'mpi_spec': spec})

# Start d4p "workflow"

@app.route('/run-d4p', methods=['POST'])
def run_d4p():
    # Load request data
    data = json.loads(request.data)
    # Check availability of PE impl
    try:
        code = butils.findPEimpl(data)
    except:
        return ('Pe not found', 404)
    # Spawn cluster
    butils.create_mpijob(data, data['n_nodes'], name_space, _d4p)
    return ('OK!', 200)

# Start specfem "workflow"

@app.route('/run-specfem', methods=['POST'])
def run_specfem():
    # Load request data
    data = json.loads(request.data)
    # Spawn specfem mpi cluster
    butils.create_specfem(data, name_space, _specfem)
    return ('OK!', 200)

#############test

@app.route('/hello', methods=['GET'])
def test():
    return ('OK!', 200)