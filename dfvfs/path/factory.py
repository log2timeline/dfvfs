# -*- coding: utf-8 -*-
"""The path specification factory."""


class Factory(object):
  """Class that implements the path specification factory."""

  PROPERTY_NAMES = frozenset([
      u'column_name',
      u'compression_method',
      u'data_stream',
      u'encoding_method',
      u'encryption_method',
      u'identifier',
      u'inode',
      u'location',
      u'mft_attribute',
      u'mft_entry',
      u'part_index',
      u'range_offset',
      u'range_size',
      u'row_condition',
      u'row_index',
      u'start_offset',
      u'store_index',
      u'table_name',
      u'volume_index'])

  _path_spec_types = {}

  _system_level_type_indicators = {}

  @classmethod
  def DeregisterPathSpec(cls, path_spec_type):
    """Deregisters a path specification.

    Args:
      path_spec_type: the path specification type (or class) object.

    Raises:
      KeyError: if path specification is not registered.
    """
    type_indicator = path_spec_type.TYPE_INDICATOR
    if type_indicator not in cls._path_spec_types:
      raise KeyError(
          u'Path specification type: {0:s} not set.'.format(type_indicator))

    del cls._path_spec_types[type_indicator]

    if type_indicator in cls._system_level_type_indicators:
      del cls._system_level_type_indicators[type_indicator]

  @classmethod
  def GetProperties(cls, path_spec):
    """Retrieves a dictionary containing the path specification properties.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Raises:
      A dictionary object containing the properties.
    """
    properties = {}

    for property_name in cls.PROPERTY_NAMES:
      # Note that we don't want to set the properties when not used.
      if hasattr(path_spec, property_name):
        properties[property_name] = getattr(path_spec, property_name)

    return properties

  @classmethod
  def IsSystemLevelTypeIndicator(cls, type_indicator):
    """Determines if the type indicator is at system-level.

    Args:
      type_indicator: the type indicator.

    Returns:
      A boolean indicating the type indicator is at system-level.
    """
    return type_indicator in cls._system_level_type_indicators

  @classmethod
  def NewPathSpec(cls, type_indicator, **kwargs):
    """Creates a new path specification for the specific type indicator.

    Args:
      type_indicator: the path specification type indicator.
      kwargs: a dictionary of keyword arguments dependending on the path
              specification.

    Returns:
      The VFS path specification (instance of PathSpec).

    Raises:
      KeyError: if path specification is not registered.
    """
    if type_indicator not in cls._path_spec_types:
      raise KeyError(
          u'Path specification type: {0:s} not set.'.format(type_indicator))

    # An empty parent will cause parentless path specifications to raise
    # so we conveniently remove it here.
    if u'parent' in kwargs and kwargs[u'parent'] is None:
      del kwargs[u'parent']

    path_spec_type = cls._path_spec_types[type_indicator]
    return path_spec_type(**kwargs)

  @classmethod
  def RegisterPathSpec(cls, path_spec_type):
    """Registers a path specification type.

    Args:
      path_spec_type: the path specification type (or class) object.

    Raises:
      KeyError: if path specification is already registered.
    """
    type_indicator = path_spec_type.TYPE_INDICATOR
    if type_indicator in cls._path_spec_types:
      raise KeyError(
          u'Path specification type: {0:s} already set.'.format(
              type_indicator))

    cls._path_spec_types[type_indicator] = path_spec_type

    if getattr(path_spec_type, u'_IS_SYSTEM_LEVEL', False):
      cls._system_level_type_indicators[type_indicator] = path_spec_type
