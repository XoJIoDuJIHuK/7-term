# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: service.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'service.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rservice.proto\x12\x07\x65xample\"$\n\x0cParm2Request\x12\t\n\x01x\x18\x01 \x01(\x05\x12\t\n\x01y\x18\x02 \x01(\x05\"\x19\n\x0cParm1Request\x12\t\n\x01x\x18\x01 \x01(\x05\".\n\x0bParm2Result\x12\t\n\x01x\x18\x01 \x01(\x05\x12\t\n\x01y\x18\x02 \x01(\x05\x12\t\n\x01z\x18\x03 \x01(\x05\"#\n\x0bParm1Result\x12\t\n\x01x\x18\x01 \x01(\x05\x12\t\n\x01z\x18\x02 \x01(\x05\x32\xd2\x02\n\x07Greeter\x12\x32\n\x03\x41\x64\x64\x12\x15.example.Parm2Request\x1a\x14.example.Parm2Result\x12\x32\n\x03Mul\x12\x15.example.Parm2Request\x1a\x14.example.Parm2Result\x12\x32\n\x03Sub\x12\x15.example.Parm2Request\x1a\x14.example.Parm2Result\x12\x32\n\x03\x44iv\x12\x15.example.Parm2Request\x1a\x14.example.Parm2Result\x12\x33\n\x04Pow2\x12\x15.example.Parm1Request\x1a\x14.example.Parm1Result\x12\x42\n\x13ReallyHeavyFunction\x12\x15.example.Parm2Request\x1a\x14.example.Parm1ResultB\x14Z\x12generated/;exampleb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z\022generated/;example'
  _globals['_PARM2REQUEST']._serialized_start=26
  _globals['_PARM2REQUEST']._serialized_end=62
  _globals['_PARM1REQUEST']._serialized_start=64
  _globals['_PARM1REQUEST']._serialized_end=89
  _globals['_PARM2RESULT']._serialized_start=91
  _globals['_PARM2RESULT']._serialized_end=137
  _globals['_PARM1RESULT']._serialized_start=139
  _globals['_PARM1RESULT']._serialized_end=174
  _globals['_GREETER']._serialized_start=177
  _globals['_GREETER']._serialized_end=515
# @@protoc_insertion_point(module_scope)
