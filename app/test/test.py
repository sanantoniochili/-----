import os
import sys
import json
import urllib.request
import requests
from urllib.error import HTTPError
from django.http import HttpResponse
import logging
import datetime
from reg_client import VerceRegClient

# Configuration of d4p registry service
d4p_service_host = os.environ['D4P_REGISTRY_SERVICE_HOST']
d4p_service_port = os.environ['D4P_REGISTRY_SERVICE_PORT']

url = 'http://' + d4p_service_host + ':' + d4p_service_port

# Configuration of dare api
dare_api_host = os.environ['NGINX_API_IP']
dare_api_port = '80'

_url = 'http://' + dare_api_host + ':' + dare_api_port

# User authentication (GETting auth token)

def authenticate(user, pasw):
	# log in registry
	logging.basicConfig()
	logger = logging.getLogger('DJREG_CLIENT')
	logger.setLevel(logging.INFO)

	# use client class
	client = VerceRegClient()
	client.manager.login(user, pasw)
	# logger.info(client.manager.get_auth_token())
	return client

# Client object init / User authentication
client = authenticate(sys.argv[1], sys.argv[2])

# Get workspace url by name

def get_workspace(name):
    # Get json response
    req = requests.get(url + '/workspaces/',
                       headers=client.manager._get_auth_header())
    resp_json = json.loads(req.text)
    # Iterate and retrieve
    return ([i['url'] for i in resp_json if i['name'] == name][0], 
            [i['id'] for i in resp_json if i['name'] == name][0]) 

# Create workspace using d4p service api

def create_workspace(clone, name, desc):
    # Prepare data for posting
    data = {
            "clone_of": clone,
            "name": name,
            "description": desc
            }
    # Request for d4p service api
    _r = requests.post(url + '/workspaces/',
                       headers=client.manager._get_auth_header(), data=data)

    # Progress check
    if _r.status_code == 201:
        print('Added workspace: ' + name)
        return get_workspace(name)
    else:
        print ('Add workspace resource returns status_code: ' + \
                str(_r.status_code))
        return get_workspace(name)

# Create ProcessingElement using d4p service api

def create_pe(desc, name, conn, pckg, workspace, clone, peimpls):
    assert isinstance(conn, list)
    assert isinstance(peimpls, list)

    # Prepare data for posting
    data = {
            "description": desc,
            "name": name,
            "connections": conn,
            "pckg": pckg,
            "workspace": workspace,
            "clone_of": clone,
            "peimpls": peimpls
           }
    # Request for d4p service api
    _r = requests.post(
        url + '/pes/', headers=client.manager._get_auth_header(), data=data)
    # Progress check
    if _r.status_code == 201:
        print('Added Processing Element: ' + name)
        return json.loads(_r.text)['url']
    else:
        print ('Add Processing Element resource returns status_code: ' + \
               str(_r.status_code))

# Create ProcessingElement Implementation using d4p service api

def create_peimpl(desc, code, parent_sig, pckg, name, workspace, clone):
    # Prepare data for posting
    data = {
            "description": desc,
            "code": code,
            "parent_sig": parent_sig,
            "pckg": pckg,
            "name": name,
            "workspace": workspace,
            "clone_of": clone
           }
    # Request for d4p service api
    _r = requests.post(url + '/peimpls/',
                       headers=client.manager._get_auth_header(), data=data)
    # Progress check
    if _r.status_code == 201:
        print('Added Processing Element Implementation: ' + name)
        return json.loads(_r.text)['id']
    else:
        print ('Add Processing Element Implementation resource returns \
                status_code: ' + str(_r.status_code))

# Spawn mpi cluster and run dispel4py workflow

def submit_d4p(impl_id, pckg, workspace_id, pe_name, n_nodes, **kw):
    # Prepare data for posting
    data = {
            "user": sys.argv[1],
            "pwd": sys.argv[2],
            "impl_id": impl_id,
            "pckg": pckg,
            "wrkspce_id": workspace_id,
            "name": pe_name,
            "n_nodes": n_nodes
            }
    d4p_args = {}
    for k in kw:
        d4p_args[k] = kw.get(k)
    data['d4p_args'] = d4p_args
    # Request for dare api
    _r = requests.post(_url + '/run-d4p', data=json.dumps(data))
    # Progress check
    if _r.status_code == 200:
        print(_r.text)
    else:
        print('DARE api resource / d4p-mpi-spec returns status_code: \
                '+str(_r.status_code))


# Spawn mpi cluster and run specfem workflow

def submit_specfem(n_nodes, data_url):
    # Prepare data for posting
    data = {
            "n_nodes": n_nodes,
            "data_url": data_url
            }
    # Request for dare api
    _r = requests.post(_url + '/run-specfem', data=json.dumps(data))
    # Progress check
    if _r.status_code == 200:
        print(_r.text)
    else:
        print('DARE api resource / d4p-mpi-spec returns status_code: \
                '+str(_r.status_code))

# DARE api test

def dare_api_test():
    if sys.argv[3] == 'd4p':
        print('Creating Workspace: TEST ......')
        # API "workflow" preprocess
        workspace_url, workspace_id=create_workspace("", "TEST", "")
        workspace_id = int(workspace_id)
        print('Creating PE:TEST in Workspace: TEST ......')
        pe_url=create_pe(desc="", name="TEST", conn=[], pckg="TEST",
                    workspace=workspace_url, clone="", peimpls=[])
        print('Creating PE Impl '+str(pe_url)+' of PE: TEST......')
        impl_id=create_peimpl(desc="", code=open('mySplitMerge.py').read(),
                                      parent_sig=pe_url, pckg="TEST",
                                      name="TEST", workspace=workspace_url,
                                      clone="")
        print('Submit Dispel4py run with non existent PE Impl. .....')
        submit_d4p(impl_id=9999, pckg="asdasda", workspace_id=9999,
                pe_name="kdasudkasl", n_nodes=6)
        print('Submit correct Dispel4py run of PE TEST .....')
        # DARE API demo
        submit_d4p(impl_id=impl_id, pckg="TEST", workspace_id=workspace_id, pe_name="TEST",
                                n_nodes=6, no_processes=6, iterations=1)
    else:
        submit_specfem(n_nodes=24,
                data_url='https://gitlab.com/project-dare/dare-api/raw/master/containers/specfem3d/data.zip')

if __name__ == '__main__':
    dare_api_test()
