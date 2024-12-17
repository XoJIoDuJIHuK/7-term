FROM python:3.12

WORKDIR /grpc-demo
COPY service.proto ./
RUN pip install grpcio grpcio-tools
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. --pyi_out=. service.proto
COPY main.py main.py

ENTRYPOINT ["python", "main.py"]