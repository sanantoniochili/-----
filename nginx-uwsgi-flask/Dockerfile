FROM nginx:latest

RUN apt-get update
RUN apt-get install -y python3 python3-pip supervisor

# install requirements

RUN pip3 install --upgrade setuptools
RUN pip3 install uwsgi
RUN pip3 install kubernetes
RUN pip3 install numpy 
RUN pip3 install flask 
RUN pip3 install cwl-runner
RUN pip3 install PyYAML
RUN pip3 install Django

# Configure servers

RUN mkdir /etc/uwsgi/
RUN rm /etc/nginx/conf.d/default.conf

COPY conf/nginx.conf /etc/nginx/nginx.conf
COPY conf/flask-nginx.conf /etc/nginx/conf.d/
COPY conf/uwsgi.ini /etc/uwsgi/
COPY conf/supervisord.conf /etc/supervisor/

# Copy the application

COPY /app /app
WORKDIR /app

# Start servers

CMD ["/usr/bin/supervisord"]