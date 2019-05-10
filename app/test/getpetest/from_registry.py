import sys, json
import urllib.request, requests
from urllib.error import HTTPError
from django.http import HttpResponse
import logging, datetime
from reg_client import VerceRegClient

def authenticate(user,pasw):
	# log in registry
	logging.basicConfig()
	logger = logging.getLogger('DJREG_CLIENT')
	logger.setLevel(logging.INFO)

	# use client class
	client = VerceRegClient()
	client.manager.login(user, pasw)
	logger.info(client.manager.get_auth_token())
	return client


def get_PE(id,wid,pckg,name,client):
	# get PE signature by <name>
	# getting implementation code from PE submission, has to be rethought
	pe = client.manager.get_pe_spec(wid, pckg, name)
	peimpls = pe['peimpls']
	code = ''
	# get pe implementation with id: <id>
	for impl in peimpls:
		id_str = impl.rsplit('/', 2)[1]
		if int(id_str) == id:
			r = requests.get(impl, headers=client.manager._get_auth_header())
			code = r.json().get('code')
	if code == '':
		raise ImplementationNotFound()
	return code
	

def get_pe_impl(id,wid,pckg,name,client):
	# get PE signature by <name>
	# getting implementation code from PE submission, has to be rethought
	pe = client.manager.get_pe_spec(wid, pckg, name)
	peimpls = pe['peimpls']
	code = ''
	# get pe implementation with id: <id>
	for impl in peimpls:
		resp_json = json.loads(requests.get(impl,
                       	headers=client.manager._get_auth_header()).text)
		if resp_json['id'] == id:
			r = requests.get(impl, 
						headers=client.manager._get_auth_header())
			code = r.json().get('code')
	if code == '':
		raise ImplementationNotFound()
	return code


class ImplementationNotFound(Exception):
	pass

