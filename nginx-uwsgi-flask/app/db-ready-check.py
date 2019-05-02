import os
import sys
import logging
from reg_client import VerceRegClient

# Configuration of d4p registry service
d4p_service_host = os.environ['D4P_REGISTRY_SERVICE_HOST']
d4p_service_port = os.environ['D4P_REGISTRY_SERVICE_PORT']

url = 'http://' + d4p_service_host + ':' + d4p_service_port

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
