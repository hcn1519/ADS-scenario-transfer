# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: modules/common_msgs/basic_msgs/geometry.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n-modules/common_msgs/basic_msgs/geometry.proto\x12\rapollo.common\"8\n\x08PointENU\x12\x0e\n\x01x\x18\x01 \x01(\x01:\x03nan\x12\x0e\n\x01y\x18\x02 \x01(\x01:\x03nan\x12\x0c\n\x01z\x18\x03 \x01(\x01:\x01\x30\"A\n\x08PointLLH\x12\x10\n\x03lon\x18\x01 \x01(\x01:\x03nan\x12\x10\n\x03lat\x18\x02 \x01(\x01:\x03nan\x12\x11\n\x06height\x18\x03 \x01(\x01:\x01\x30\")\n\x07Point2D\x12\x0e\n\x01x\x18\x01 \x01(\x01:\x03nan\x12\x0e\n\x01y\x18\x02 \x01(\x01:\x03nan\"9\n\x07Point3D\x12\x0e\n\x01x\x18\x01 \x01(\x01:\x03nan\x12\x0e\n\x01y\x18\x02 \x01(\x01:\x03nan\x12\x0e\n\x01z\x18\x03 \x01(\x01:\x03nan\"P\n\nQuaternion\x12\x0f\n\x02qx\x18\x01 \x01(\x01:\x03nan\x12\x0f\n\x02qy\x18\x02 \x01(\x01:\x03nan\x12\x0f\n\x02qz\x18\x03 \x01(\x01:\x03nan\x12\x0f\n\x02qw\x18\x04 \x01(\x01:\x03nan\"0\n\x07Polygon\x12%\n\x05point\x18\x01 \x03(\x0b\x32\x16.apollo.common.Point3D')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'modules.common_msgs.basic_msgs.geometry_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_POINTENU']._serialized_start=64
  _globals['_POINTENU']._serialized_end=120
  _globals['_POINTLLH']._serialized_start=122
  _globals['_POINTLLH']._serialized_end=187
  _globals['_POINT2D']._serialized_start=189
  _globals['_POINT2D']._serialized_end=230
  _globals['_POINT3D']._serialized_start=232
  _globals['_POINT3D']._serialized_end=289
  _globals['_QUATERNION']._serialized_start=291
  _globals['_QUATERNION']._serialized_end=371
  _globals['_POLYGON']._serialized_start=373
  _globals['_POLYGON']._serialized_end=421
# @@protoc_insertion_point(module_scope)
