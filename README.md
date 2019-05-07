# nginx-flask-api

This project's purpose is to form the serving environment of the application contained in "app" folder on the basis of the official nginx image (https://hub.docker.com/_/nginx/).
Docker-compose yaml provided for testing with already uploaded images.

## Folders

* conf [configuration files]
    * nginx 
    * uwsgi 
    * supervisord 
    
* app [with flask]
    * run.py
    * etc

## App

The particular folder contains an application developed for the needs of DARE api (https://gitlab.com/project-dare/dare-api).

