# -*- coding: utf-8 -*-
"""The protobuf serializer object implementation."""

from dfvfs.path import factory as path_spec_factory
from dfvfs.proto import transmission_pb2
from dfvfs.serializer import serializer


class ProtobufPathSpecSerializer(serializer.PathSpecSerializer):
  """Class that implements a protobuf path specification serializer object."""

  @classmethod
  def ReadSerializedRowCondtion(cls, proto):
    """Reads a row_condition from serialized form.

    Args:
      proto: a protobuf object (instance of transmission_pb2.RowCondition)
             containing the serialized form.

    Returns:
      A row_condition tuple (left_operand, operator, right_operand).

    Raises:
      RuntimeError: when proto is not of type: transmission_pb2.RowCondition.
    """
    if not isinstance(proto, transmission_pb2.RowCondition):
      raise RuntimeError(u'Unsupported serialized type.')

    left_operand = u''
    operator = u''
    right_operand = u''
    for proto_attribute, value in proto.ListFields():
      if proto_attribute.name == u'left_operand':
        left_operand = value
      elif proto_attribute.name == u'operator':
        operator = value
      elif proto_attribute.name == u'right_operand':
        right_operand = value
    return left_operand, operator, right_operand

  @classmethod
  def ReadSerializedObject(cls, proto):
    """Reads a path specification from serialized form.

    Args:
      proto: a protobuf object (instance of transmission_pb2.PathSpec)
             containing the serialized form.

    Returns:
      A path specification (instance of PathSpec).

    Raises:
      RuntimeError: when proto is not of type: transmission_pb2.PathSpec.
    """
    if not isinstance(proto, transmission_pb2.PathSpec):
      raise RuntimeError(u'Unsupported serialized type.')

    # Note that we don't want to set the keyword arguments when not used because
    # the path specification base class will check for unused keyword arguments
    # and raise.
    type_indicator = u''
    kwargs = {}

    for proto_attribute, value in proto.ListFields():
      if proto_attribute.name == u'type_indicator':
        type_indicator = value
      elif proto_attribute.name == u'parent':
        kwargs[u'parent'] = cls.ReadSerializedObject(value)
      elif proto_attribute.name == u'row_condition':
        kwargs[u'row_condition'] = cls.ReadSerializedRowCondtion(value)
      elif proto_attribute.name in path_spec_factory.Factory.PROPERTY_NAMES:
        kwargs[proto_attribute.name] = value

    return path_spec_factory.Factory.NewPathSpec(type_indicator, **kwargs)

  @classmethod
  def ReadSerialized(cls, proto_string):
    """Reads a path specification from serialized form.

    Args:
      proto_string: a protobuf string containing the serialized form.

    Returns:
      A path specification (instance of PathSpec).
    """
    proto = transmission_pb2.PathSpec()
    proto.ParseFromString(proto_string)

    return cls.ReadSerializedObject(proto)

  @classmethod
  def WriteSerializedObject(cls, path_spec):
    """Writes a path specification to serialized form.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      A protobuf object (instance of (transmission_pb2.PathSpec)
      containing the serialized form.
    """
    serialized = transmission_pb2.PathSpec()
    serialized.type_indicator = path_spec.type_indicator

    if path_spec.HasParent():
      serialized_parent = cls.WriteSerializedObject(path_spec.parent)
      serialized.parent.MergeFrom(serialized_parent)

    # We don't want to set attributes here that are not used.
    for property_name in path_spec_factory.Factory.PROPERTY_NAMES:
      if hasattr(path_spec, property_name):
        property_value = getattr(path_spec, property_name, None)
        if property_value is not None:
          # Convert row_condition tuple to transmission_pb2.RowCondition
          if property_name == u'row_condition':
            serialized.row_condition.left_operand = property_value[0]
            serialized.row_condition.operator = property_value[1]
            serialized.row_condition.right_operand = property_value[2]
          else:
            setattr(serialized, property_name, property_value)

    return serialized

  @classmethod
  def WriteSerialized(cls, path_spec):
    """Writes a path specification to serialized form.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      A protobuf string containing the serialized form.
    """
    proto = cls.WriteSerializedObject(path_spec)
    return proto.SerializeToString()
