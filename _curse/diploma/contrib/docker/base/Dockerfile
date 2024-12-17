FROM python:3.12

WORKDIR /app
ENV PYTHONPATH=/app

COPY contrib/docker/wait-for-it.sh wait-for-it.sh
COPY contrib/docker/docker-entrypoint.sh docker-entrypoint.sh
RUN chmod +x wait-for-it.sh \
    && chmod +x docker-entrypoint.sh \
    && mkdir docker-entrypoint.d

COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade -r /app/requirements.txt

COPY . .

ENTRYPOINT ["/app/docker-entrypoint.sh"]