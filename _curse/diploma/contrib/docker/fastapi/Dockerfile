FROM diploma-base

#COPY contrib/docker/fastapi/docker-entrypoint.d /app/docker-entrypoint.d

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]