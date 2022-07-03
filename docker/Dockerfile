FROM python:3.8.12-slim-bullseye

ARG proxy
ARG no_proxy

ENV http_proxy=$proxy
ENV https_proxy=$proxy
ENV NO_PROXY=$no_proxy

RUN apt update && apt install -y curl jq
RUN curl -sL https://deb.nodesource.com/setup_lts.x | bash -
RUN apt update && \
    apt install -y nodejs && \
    apt clean

RUN mkdir -p /opt/work/cdk_template
WORKDIR /opt/work

RUN npm update -g npm && npm install -g aws-cdk@2.30.0
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir -p /opt/cdk
WORKDIR /opt/cdk