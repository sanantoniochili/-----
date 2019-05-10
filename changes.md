# Changes in app/ folder

### Added conf/ folder 
Servers' configuration

### get_PE() to get_pe_impl()
- _Affects backend_utils.py, from_registry.py_

More trustworthy implementation giving same results. Check for validation in getpetest/ folder. 

### env var NGINX-API-IP to NGINX_API_IP
- _Affects test.py_

Only for docker-compose testing purposes

### data = json.loads(request.data) to  data = json.loads(request.data.decode('utf-8'))
- _Affects run.py_

Otherwise won't run
