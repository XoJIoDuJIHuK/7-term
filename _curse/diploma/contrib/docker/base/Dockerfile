FROM python:3.12

WORKDIR /app
ENV PYTHONPATH=/app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade -r /app/requirements.txt

COPY ./ /app/