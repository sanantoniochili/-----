FROM nginx:alpine

EXPOSE 80

# replace default configuration
RUN rm /etc/nginx/nginx.conf
COPY ./nginx.conf /etc/nginx/nginx.conf