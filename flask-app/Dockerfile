FROM alpine:3.7

RUN apk add --no-cache \
        uwsgi-python3 \
        python3

COPY ./app /app
WORKDIR app

EXPOSE 8080

CMD ["uwsgi", "--ini", "uwsgi.ini"]
