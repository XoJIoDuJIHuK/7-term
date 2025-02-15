# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import service_pb2 as service__pb2

GRPC_GENERATED_VERSION = '1.68.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in service_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class GreeterStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Add = channel.unary_unary(
                '/example.Greeter/Add',
                request_serializer=service__pb2.Parm2Request.SerializeToString,
                response_deserializer=service__pb2.Parm2Result.FromString,
                _registered_method=True)
        self.Mul = channel.unary_unary(
                '/example.Greeter/Mul',
                request_serializer=service__pb2.Parm2Request.SerializeToString,
                response_deserializer=service__pb2.Parm2Result.FromString,
                _registered_method=True)
        self.Sub = channel.unary_unary(
                '/example.Greeter/Sub',
                request_serializer=service__pb2.Parm2Request.SerializeToString,
                response_deserializer=service__pb2.Parm2Result.FromString,
                _registered_method=True)
        self.Div = channel.unary_unary(
                '/example.Greeter/Div',
                request_serializer=service__pb2.Parm2Request.SerializeToString,
                response_deserializer=service__pb2.Parm2Result.FromString,
                _registered_method=True)
        self.Pow2 = channel.unary_unary(
                '/example.Greeter/Pow2',
                request_serializer=service__pb2.Parm1Request.SerializeToString,
                response_deserializer=service__pb2.Parm1Result.FromString,
                _registered_method=True)
        self.ReallyHeavyFunction = channel.unary_unary(
                '/example.Greeter/ReallyHeavyFunction',
                request_serializer=service__pb2.Parm2Request.SerializeToString,
                response_deserializer=service__pb2.Parm1Result.FromString,
                _registered_method=True)


class GreeterServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Add(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Mul(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Sub(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Div(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Pow2(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReallyHeavyFunction(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_GreeterServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Add': grpc.unary_unary_rpc_method_handler(
                    servicer.Add,
                    request_deserializer=service__pb2.Parm2Request.FromString,
                    response_serializer=service__pb2.Parm2Result.SerializeToString,
            ),
            'Mul': grpc.unary_unary_rpc_method_handler(
                    servicer.Mul,
                    request_deserializer=service__pb2.Parm2Request.FromString,
                    response_serializer=service__pb2.Parm2Result.SerializeToString,
            ),
            'Sub': grpc.unary_unary_rpc_method_handler(
                    servicer.Sub,
                    request_deserializer=service__pb2.Parm2Request.FromString,
                    response_serializer=service__pb2.Parm2Result.SerializeToString,
            ),
            'Div': grpc.unary_unary_rpc_method_handler(
                    servicer.Div,
                    request_deserializer=service__pb2.Parm2Request.FromString,
                    response_serializer=service__pb2.Parm2Result.SerializeToString,
            ),
            'Pow2': grpc.unary_unary_rpc_method_handler(
                    servicer.Pow2,
                    request_deserializer=service__pb2.Parm1Request.FromString,
                    response_serializer=service__pb2.Parm1Result.SerializeToString,
            ),
            'ReallyHeavyFunction': grpc.unary_unary_rpc_method_handler(
                    servicer.ReallyHeavyFunction,
                    request_deserializer=service__pb2.Parm2Request.FromString,
                    response_serializer=service__pb2.Parm1Result.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'example.Greeter', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('example.Greeter', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class Greeter(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Add(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/example.Greeter/Add',
            service__pb2.Parm2Request.SerializeToString,
            service__pb2.Parm2Result.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Mul(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/example.Greeter/Mul',
            service__pb2.Parm2Request.SerializeToString,
            service__pb2.Parm2Result.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Sub(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/example.Greeter/Sub',
            service__pb2.Parm2Request.SerializeToString,
            service__pb2.Parm2Result.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Div(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/example.Greeter/Div',
            service__pb2.Parm2Request.SerializeToString,
            service__pb2.Parm2Result.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Pow2(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/example.Greeter/Pow2',
            service__pb2.Parm1Request.SerializeToString,
            service__pb2.Parm1Result.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ReallyHeavyFunction(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/example.Greeter/ReallyHeavyFunction',
            service__pb2.Parm2Request.SerializeToString,
            service__pb2.Parm1Result.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
