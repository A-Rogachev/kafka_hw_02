FROM python:3.11-slim

WORKDIR /opt

ENV PYTHONPATH=/opt:$PYTHONPATH

COPY requirements.txt ./
RUN  pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

COPY app ./app