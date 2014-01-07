#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The dfVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The protobuf serializer object implementation."""

from dfvfs.path import factory as path_spec_factory
from dfvfs.proto import transmission_pb2
from dfvfs.serializer import serializer


class ProtobufPathSpecSerializer(serializer.PathSpecSerializer):
  """Class that implements a protobuf path specification serializer object."""

  @classmethod
  def ReadSerialized(cls, proto):
    """Reads a path specification from serialized form.

    Args:
      proto: a protobuf object (instance of transmission_pb2.PathSpec)
             containing the serialized form.

    Returns:
      A path specification (instance of path.PathSpec).

    Raises:
      RuntimeError: when proto is not of type: transmission_pb2.PathSpec.
    """
    if not isinstance(proto, transmission_pb2.PathSpec):
      raise RuntimeError('Unsupported serialized type.')

    # Note that we don't want to set the keyword arguments when not used because
    # the path specification base class will check for unused keyword arguments
    # and raise.
    type_indicator = u''
    kwargs = {}

    for proto_attribute, value in proto.ListFields():
      if proto_attribute.name == 'type_indicator':
        type_indicator = value
      elif proto_attribute.name == 'parent':
        kwargs['parent'] = cls.ReadSerialized(value)
      elif proto_attribute.name in path_spec_factory.Factory.PROPERTY_NAMES:
        kwargs[proto_attribute.name] = value

    return path_spec_factory.Factory.NewPathSpec(type_indicator, **kwargs)

  @classmethod
  def WriteSerialized(cls, path_spec):
    """Writes a path specification to serialized form.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A protobuf object (instance of (transmission_pb2.PathSpec)
      containing the serialized form.
    """
    serialized = transmission_pb2.PathSpec()
    serialized.type_indicator = path_spec.type_indicator

    if path_spec.HasParent():
      serialized_parent = cls.WriteSerialized(path_spec.parent)
      serialized.parent.MergeFrom(serialized_parent)

    # We don't want to set attributes here that are not used.
    for property_name in path_spec_factory.Factory.PROPERTY_NAMES:
      if hasattr(path_spec, property_name):
        property_value = getattr(path_spec, property_name, None)
        if property_value is not None:
          setattr(serialized, property_name, property_value)

    return serialized
