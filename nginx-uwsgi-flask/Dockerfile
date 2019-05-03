FROM nginx:latest

RUN apt-get update
RUN apt-get install -y python3 python3-pip supervisor

RUN pip3 install --upgrade setuptools
RUN pip3 install uwsgi

# install requirements
RUN pip3 install kubernetes
RUN pip3 install numpy 
RUN pip3 install flask 
RUN pip3 install cwl-runner
RUN pip3 install PyYAML
RUN pip3 install Django

# Set up servers
RUN mkdir /etc/uwsgi/

COPY flask-nginx.conf /etc/nginx/conf.d/
COPY uwsgi.ini /etc/uwsgi/
COPY supervisord.conf /etc/supervisor/

# Copy the application
COPY /app /app

WORKDIR /app

CMD ["/usr/bin/supervisord"]