FROM python:2.7-alpine

RUN pip install --upgrade pip && \
    mkdir -p /srv/src

WORKDIR /srv/src

ADD ./src/requirements.txt /srv/src/requirements.txt

RUN pip install -r requirements.txt

ADD ./src /srv/src
