# Changes in app/ folder

### Added conf/ folder 
Servers' configuration

### get_PE() to get_pe_impl()
- Affects backend_utils.py, from_registry.py
More trustworthy implementation giving same results. Check for validation in getpetest/ folder. 

### env var NGINX-API-IP to NGINX_API_IP
- Affects test.py 
Only for docker-compose testing purposes

### data = json.loads(request.data) to  data = json.loads(request.data.decode('utf-8'))
- Affects run.py
Otherwise won't run
