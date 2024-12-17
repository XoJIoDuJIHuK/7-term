import asyncio
import os

from grpc._channel import _InactiveRpcError
import grpc
from grpc.aio import AioRpcError

import service_pb2
import service_pb2_grpc


server_host = os.environ.get('GRPC_SERVER_HOST', 'localhost')
server_port = os.environ.get('GRPC_SERVER_PORT', '50051')


def run():
    with grpc.insecure_channel(f'{server_host}:{server_port}') as channel:
        stub = service_pb2_grpc.GreeterStub(channel)
        response = stub.Add(service_pb2.Parm2Request(x=10, y=5))
        print(f"{response.x} + {response.y} = {response.z}")
        response = stub.Sub(service_pb2.Parm2Request(x=10, y=5))
        print(f"{response.x} - {response.y} = {response.z}")
        response = stub.Mul(service_pb2.Parm2Request(x=10, y=5))
        print(f"{response.x} * {response.y} = {response.z}")
        response = stub.Div(service_pb2.Parm2Request(x=10, y=5))
        print(f"{response.x} / {response.y} = {response.z}")
        try:
            x = 3
            print(f"Pow {x} ^ 2 = ", end="")
            response = stub.Pow2(service_pb2.Parm1Request(x=3), timeout=3)
            print(response.z)
        except _InactiveRpcError as e:
            print(f"{e.details()}")
        try:
            print('Timeout example')
            response = stub.ReallyHeavyFunction(service_pb2.Parm1Request(x=2), timeout=1.0)
            print(f"Result: {response.z}")
        except _InactiveRpcError as e:
            print(f"{e.args[0].code}: {e.details()}")


async def arun():
    async with grpc.aio.insecure_channel(f'{server_host}:{server_port}') as channel:
        stub = service_pb2_grpc.GreeterStub(channel)
        response = await stub.Add(service_pb2.Parm2Request(x=45, y=5))
        print(f"{response.x} + {response.y} = {response.z}")
        response = await stub.Sub(service_pb2.Parm2Request(x=12, y=5))
        print(f"{response.x} - {response.y} = {response.z}")
        response = await stub.Mul(service_pb2.Parm2Request(x=5, y=5))
        print(f"{response.x} * {response.y} = {response.z}")
        response = await stub.Div(service_pb2.Parm2Request(x=76, y=5))
        print(f"{response.x} / {response.y} = {response.z}")
        response = await stub.Pow2(service_pb2.Parm1Request(x=12))
        print(f"{response.x} ^ 2 = {response.z}")
        try:
            response = await stub.Div(service_pb2.Parm2Request(x=12, y=0))
            print(f"Zero div: {response.z}")
        except AioRpcError as e:
            print(f'AIO RPC ERROR: {e.details()}')
        try:
            print("Cancellation example")
            future = stub.ReallyHeavyFunction(
                service_pb2.Parm1Request(x=2),
                # timeout=1.0,
                wait_for_ready=True
            )
            await asyncio.sleep(1)
            future.cancel()
            print(await future.details())
        except _InactiveRpcError as e:
            print(f"{e.args[0].code}: {e.details()}")

if __name__ == '__main__':
    print('Running sync')
    run()
    print('Running async')
    asyncio.run(arun())
