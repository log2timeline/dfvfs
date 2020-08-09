# -*- coding: utf-8 -*-
"""The path specification factory."""

from __future__ import unicode_literals


class Factory(object):
  """Path specification factory."""

  PROPERTY_NAMES = frozenset([
      'cipher_mode',
      'column_name',
      'compression_method',
      'data_stream',
      'encoding_method',
      'encryption_method',
      'identifier',
      'initialization_vector',
      'inode',
      'key',
      'location',
      'mft_attribute',
      'mft_entry',
      'part_index',
      'password',
      'range_offset',
      'range_size',
      'recovery_password',
      'row_condition',
      'row_index',
      'start_offset',
      'startup_key',
      'store_index',
      'table_name',
      'volume_index'])

  _path_spec_types = {}

  _system_level_type_indicators = {}

  @classmethod
  def DeregisterPathSpec(cls, path_spec_type):
    """Deregisters a path specification type.

    Args:
      path_spec_type (type): path specification type.

    Raises:
      KeyError: if path specification type is not registered.
    """
    type_indicator = path_spec_type.TYPE_INDICATOR
    if type_indicator not in cls._path_spec_types:
      raise KeyError('Path specification type: {0:s} not set.'.format(
          type_indicator))

    del cls._path_spec_types[type_indicator]

    if type_indicator in cls._system_level_type_indicators:
      del cls._system_level_type_indicators[type_indicator]

  @classmethod
  def GetProperties(cls, path_spec):
    """Retrieves a dictionary containing the path specification properties.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      dict[str, str]: path specification properties.

    Raises:
      dict: path specification properties.
    """
    properties = {}

    for property_name in cls.PROPERTY_NAMES:
      # Note that we do not want to set the properties when not used.
      if hasattr(path_spec, property_name):
        properties[property_name] = getattr(path_spec, property_name)

    return properties

  @classmethod
  def IsSystemLevelTypeIndicator(cls, type_indicator):
    """Determines if the type indicator is at system-level.

    Args:
      type_indicator (str): type indicator.

    Returns:
      bool: True if the type indicator is at system-level.
    """
    return type_indicator in cls._system_level_type_indicators

  @classmethod
  def NewPathSpec(cls, type_indicator, **kwargs):
    """Creates a new path specification for the specific type indicator.

    Args:
      type_indicator (str): type indicator.
      kwargs (dict): keyword arguments depending on the path specification.

    Returns:
      PathSpec: path specification.

    Raises:
      KeyError: if path specification is not registered.
    """
    if type_indicator not in cls._path_spec_types:
      raise KeyError('Path specification type: {0:s} not set.'.format(
          type_indicator))

    # An empty parent will cause parentless path specifications to raise
    # so we conveniently remove it here.
    if 'parent' in kwargs and kwargs['parent'] is None:
      del kwargs['parent']

    path_spec_type = cls._path_spec_types[type_indicator]
    return path_spec_type(**kwargs)

  @classmethod
  def RegisterPathSpec(cls, path_spec_type):
    """Registers a path specification type.

    Args:
      path_spec_type (type): path specification type.

    Raises:
      KeyError: if path specification type is already registered.
    """
    type_indicator = path_spec_type.TYPE_INDICATOR
    if type_indicator in cls._path_spec_types:
      raise KeyError('Path specification type: {0:s} already set.'.format(
          type_indicator))

    cls._path_spec_types[type_indicator] = path_spec_type

    if getattr(path_spec_type, '_IS_SYSTEM_LEVEL', False):
      cls._system_level_type_indicators[type_indicator] = path_spec_type
