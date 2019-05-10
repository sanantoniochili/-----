
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

# Get workspace url by name

def get_workspace(name):
    # Get json response
    req = requests.get(url + '/workspaces/',
                       headers=client.manager._get_auth_header())
    resp_json = json.loads(req.text)
    # Iterate and retrieve
    return ([i['url'] for i in resp_json if i['name'] == name][0], 
            [i['id'] for i in resp_json if i['name'] == name][0]) 

# Delete workspace by name

def delete_workspace(name):
        '''Delete a PE sig / specification by workspace, package and name.'''
        url = get_workspace(name)
        r2 = requests.delete(url, headers=client.manager._get_auth_header())

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

# # Create ProcessingElement Implementation using d4p service api

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

from backend_utils import findPEimpl
from from_registry import get_PE, get_pe_impl
# from reg_lib import VerceRegManager as VRM

def dare_api_test():
    # Create Workspaces
    print('Creating Workspaces 1 & 2......')
    workspace_url1, workspace_id1=create_workspace("", "1", "")
    workspace_id1 = int(workspace_id1)

    workspace_url2, workspace_id2=create_workspace("", "2", "")
    workspace_id2 = int(workspace_id2)

    name1=sys.argv[3]
    pckg1=sys.argv[3]
    name2=sys.argv[4]
    pckg2=sys.argv[4]

    # Create PE 
    pe_url1=create_pe(desc="", name=name1, conn=[], pckg=pckg1,
                workspace=workspace_url1, clone="", peimpls=[])
    # Add Impls
    impl_id=create_peimpl(desc="", code="PE1impl1",
                                  parent_sig=pe_url1, pckg=pckg1,
                                  name=name1, workspace=workspace_url1,
                                  clone="")
    impl_id=create_peimpl(desc="", code="PE1impl2",
                                  parent_sig=pe_url1, pckg=pckg2,
                                  name=name1, workspace=workspace_url1,
                                  clone="")

    # Create PE 
    pe_url2=create_pe(desc="", name=name2, conn=[], pckg=pckg2,
                workspace=workspace_url2, clone="", peimpls=[])
    # Add Impl
    impl_id=create_peimpl(desc="", code="PE2impl1",
                                  parent_sig=pe_url2, pckg=pckg2,
                                  name=name2, workspace=workspace_url2,
                                  clone="")

    # Mix order of implementations
    # First PE
    impl_id=create_peimpl(desc="", code="PE1impl3",
                                  parent_sig=pe_url1, pckg=pckg1,
                                  name=name1, workspace=workspace_url2,
                                  clone="")
    # Seconde PE
    impl_id=create_peimpl(desc="", code="PE2impl2",
                                  parent_sig=pe_url2, pckg=pckg2,
                                  name=name2, workspace=workspace_url1,
                                  clone="")

    
    print("-----------original")
    # id, workspace_id, pckg, name, self
    print(get_pe_impl(4,workspace_id1,pckg1,name1,client))
    print(get_pe_impl(1,workspace_id1,pckg1,name1,client))
    print(get_pe_impl(5,workspace_id2,pckg2,name2,client))
    print(get_pe_impl(3,workspace_id2,pckg2,name2,client))
    print(get_pe_impl(2,workspace_id1,pckg1,name1,client))

    print("-----------new")
    # id, workspace_id, pckg, name, self
    print(get_PE(4,workspace_id1,pckg1,name1,client))
    print(get_PE(1,workspace_id1,pckg1,name1,client))
    print(get_PE(5,workspace_id2,pckg2,name2,client))
    print(get_PE(3,workspace_id2,pckg2,name2,client))
    print(get_PE(2,workspace_id1,pckg1,name1,client))



if __name__ == '__main__':
    dare_api_test()