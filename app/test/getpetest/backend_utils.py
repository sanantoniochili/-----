import argparse
from importlib import import_module
import os, json
from from_registry import authenticate, get_pe_impl
from kubernetes import client, config, utils
from kubernetes.client.rest import ApiException

import threading


# Create yaml specification for cwl run of dispel4py

def mpi_input(workflow, **kw):
    output_data = {
        'd4py': 'dispel4py',
        'target': 'mpi',
        'workflow': workflow,
    }
    for k in kw:
        output_data[k] = kw.get(k)
    return output_data

# Return $HOSTNAME pod (current pod running this code)


def init_from_yaml(name_space):
    # Rbac authorization for inter container kubectl api calls
    config.load_incluster_config()
    # Init client
    v1 = client.CoreV1Api()
    # Get pods in dare-api namespace
    ret = v1.list_namespaced_pod(name_space)
    # Find ngix-api pod
    for i in ret.items:
        if i.metadata.name == os.environ['HOSTNAME']:
            return i


# Monitor d4p mpi cluster

def monitor(name_space, jobname):
    # Rbac authorization for inter container kubectl api calls
    config.load_incluster_config()
    while True:
            # Init client
        v1 = client.CoreV1Api()
        # Get pods in dare-api namespace
        ret = v1.list_namespaced_pod(name_space)
        # For each pod
        for i in ret.items:
            # Check if mpi cluster has been initialized
            if jobname + '-launcher' in i.metadata.name:
                # If mpijob is finished, then delete cluster
                if i.status.phase == 'Succeeded':
                    api_instance = client.CustomObjectsApi(client.ApiClient())
                    # MPIJOB specifics
                    group = 'kubeflow.org'
                    version = 'v1alpha1'
                    plural = 'mpijobs'
                    name = jobname
                    body = client.V1DeleteOptions()
                    grace_period_seconds = 0
                    orphan_dependents = True
                    # Delete mpi cluster
                    try:
                        api_instance.delete_namespaced_custom_object(group,
                                                                     version, name_space, plural, name, body)
                    except:
                        break
                    break

# Monitor specfem mpi cluster


def specfem_monitor(name_space, specname):
    # Rbac authorization for inter container kubectl api calls
    config.load_incluster_config()
    while True:
        # Init client
        v1 = client.CoreV1Api()
        # Get pods in dare-api namespace
        ret = v1.list_namespaced_pod(name_space)
        # For each pod
        for i in ret.items:
            # Check if mpi cluster has been initialized
            if specname + '-launcher' in i.metadata.name:
                # If mpijob is finished, then delete cluster
                if i.status.phase == 'Succeeded':
                    api_instance = client.CustomObjectsApi(client.ApiClient())
                    # MPIJOB specifics
                    group = 'kubeflow.org'
                    version = 'v1alpha1'
                    plural = 'mpijobs'
                    name = specname
                    body = client.V1DeleteOptions()
                    grace_period_seconds = 0
                    orphan_dependents = True
                    # Delete mpi cluster
                    try:
                        api_instance.delete_namespaced_custom_object(group,
                                                                     version, name_space, plural, name, body)
                    except:
                        break
                    break


# Retrieve python implementation of specific ProcessingElement from registry

def findPEimpl(data):
    # Authenticate user / GET auth token
    client = authenticate(data['user'], data['pwd'])
    # Get ProcessingElement Implementation code
    code = get_pe_impl(data['impl_id'],
                  data['wrkspce_id'],
                  data['pckg'],
                  data['name'],
                  client)
    return code


# Define d4p mpi cluster deployment in kubernetes


def create_mpijob(data, n_nodes, name_space, _d4p):
    # Rbac authorization for inter container kubectl api calls
    config.load_incluster_config()
    # create an instance of the API class
    api_instance = client.CustomObjectsApi(client.ApiClient())
    # MPIJOB specifics
    group = 'kubeflow.org'
    version = 'v1alpha1'
    plural = 'mpijobs'
    mpijob_json = \
        '''{  "apiVersion":"kubeflow.org/v1alpha1",
          "kind":"MPIJob",
          "metadata":{
            "name":"%s",
            "namespace":"%s"
          },
          "spec":{
            "replicas": %d,
            "template":{
              "spec":{
                "containers":[
                  {
                    "image":"registry.gitlab.com/project-dare/dare-api/d4p-openmpi-cwl:latest",
                    "imagePullPolicy":"Always",
                    "name":"%s",
                    "env":[
                      {
                        "name":"NGINX_API_SERVICE_HOST",
                        "value":"%s"
                      },
                      {
                        "name":"NGINX_API_SERVICE_PORT",
                        "value":"%s"
                      },
                      {
                        "name": "D4P_RUN_DATA",
                        "value": "%s"
                      }
                    ],
                    "volumeMounts":[
                      {
                        "name":"%s",
                        "mountPath":"%s"
                      }
                    ]
                  }
                ],
                "volumes":[
                  {
                    "name":"%s",
                    "flexVolume":{
                      "driver":"ceph.rook.io/rook",
                      "fsType":"ceph",
                      "options":{
                        "fsName":"%s",
                        "clusterNamespace":"rook-ceph"
                      }
                    }
                  }
                ]
              }
            }
          }
        }''' % (_d4p['jobname'], name_space, n_nodes, _d4p['jobname'],
                os.environ['NGINX-API-IP'], os.environ['NGINX-API-PORT'],
                json.dumps(json.dumps(data))[1:-1], _d4p['mountname'], _d4p['mountpath'],
                _d4p['volname'], _d4p['fsname'])
    body = json.loads(mpijob_json)
    try:
        api_response = api_instance.create_namespaced_custom_object(group,
                                                                    version, name_space, plural, body)
        print("Created mpi cluster !")
        # Monitor cluster status
        _th = threading.Thread(target=monitor, args=[name_space, _d4p['jobname']])
        _th.start()
        return 200
    except Exception as e:
        return (e, 500)

# Create specfem mpijob


def create_specfem(data, name_space, _specfem):
    # Rbac authorization for inter container kubectl api calls
    config.load_incluster_config()
    # create an instance of the API class
    api_instance = client.CustomObjectsApi(client.ApiClient())
    # MPIJOB specifics
    group = 'kubeflow.org'
    version = 'v1alpha1'
    plural = 'mpijobs'
    specfem_body_json = \
        '''{    "apiVersion":"kubeflow.org/v1alpha1",
          "kind":"MPIJob",
          "metadata":{
            "name":"%s",
            "namespace":"%s"
          },
          "spec":{
            "replicas":%d,
            "template":{
              "spec":{
                "containers":[
                  {
                    "image":"registry.gitlab.com/project-dare/dare-api/specfem3d-wp6:latest",
                    "imagePullPolicy":"Always",
                    "name":"%s",
                    "env": [
                        {
                        "name":"DATA_URL",
                        "value":"%s"
                        }
                    ],
                    "volumeMounts":[
                      {
                        "name":"%s",
                        "mountPath":"%s"
                      }
                    ]
                  }
                ],
                "volumes":[
                  {
                    "name":"%s",
                    "flexVolume":{
                      "driver":"ceph.rook.io/rook",
                      "fsType":"ceph",
                      "options":{
                        "fsName":"%s",
                        "clusterNamespace":"rook-ceph"
                      }
                    }
                  }
                ]
              }
            }
          }
        }''' % (_specfem['specname'], name_space, data['n_nodes'],
            _specfem['specvolname'], data['data_url'], _specfem['specvolname'],
            _specfem['spec_mountpath'], _specfem['specvolname'],
                _specfem['fsname'])
    body = json.loads(specfem_body_json)
    try:
        api_response = api_instance.create_namespaced_custom_object(group,
                                                                    version, name_space, plural, body)
        # Monitor cluster status
        _th = threading.Thread(target=specfem_monitor, args=[name_space, _specfem['specname']])
        _th.start()
    except Exception as e:
        return (e, 500)

# ============================================================================
# Deprecated?
# ============================================================================
#  def reg_parser():
    #  # parser to create edge on graph
    #  parser = argparse.ArgumentParser(
        #  description='Get workflow PE from registry')
    #  parser.add_argument('-user', '--user', metavar='user', type=str,
                    #  help='Set username for registry')
    #  parser.add_argument('-passw', '--passw', metavar='passw', type=str,
                    #  help='Set password for registry')
    #  parser.add_argument('-id', '--implID', metavar='implid', type=int,
                    #  help='Load workflow from PE implementation with id')
    #  parser.add_argument('-wid', '--workflowID', metavar='workid', type=int,
                    #  help='Get from workflow ID')
    #  parser.add_argument('-pckg', '--package', metavar='pckg', type=str,
                    #  help='Get from package')
    #  parser.add_argument('-nm', '--name', metavar='name', type=str,
                    #  help='Name of workflow PE')
    #  return parser
#
#  def mpi_yaml_parser():
    #  # parser to create edge on graph
    #  parser = argparse.ArgumentParser(
        #  description='Get specs for yaml file [input to cwl]')
    #  parser.add_argument('-n', '--no_processes', metavar='no_processes', type=int,
                    #  help='Set process number')
    #  parser.add_argument('-p', '--path', metavar='path', type=str,
                    #  help='Set path of module file')
    #  parser.add_argument('-i', '--iters', metavar='iters', type=int,
                    #  help='Set number of iterations')
    #  return parser
#
#  def module_parser():
    #  parser = argparse.ArgumentParser(
        #  description='Submit module from dispel4py graph')
    #  parser.add_argument('-mod', '--module', metavar='module-name',
                    #  help='module that creates a dispel4py graph '
                    #  '(python module or file name)')
    #  return parser
#
#  def find(name, path):
    #  for root, dirs, files in os.walk(path):
        #  if name in files:
            #  return os.path.join(root, name)
