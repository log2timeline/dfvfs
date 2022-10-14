# -*- coding: utf-8 -*-
"""The volume system factory."""


class Factory(object):
  """Volume system factory."""

  _volume_system_types = {}

  @classmethod
  def DeregisterVolumeSystem(cls, volume_system_type):
    """Deregisters a path specification type.

    Args:
      volume_system_type (type): path specification type.

    Raises:
      KeyError: if path specification type is not registered.
    """
    type_indicator = volume_system_type.TYPE_INDICATOR
    if type_indicator not in cls._volume_system_types:
      raise KeyError(f'Volume system type: {type_indicator:s} not set.')

    del cls._volume_system_types[type_indicator]

  @classmethod
  def NewVolumeSystem(cls, type_indicator):
    """Creates a new path specification for the specific type indicator.

    Args:
      type_indicator (str): type indicator.

    Returns:
      VolumeSystem: path specification.

    Raises:
      KeyError: if path specification is not registered.
    """
    if type_indicator not in cls._volume_system_types:
      raise KeyError(f'Volume system type: {type_indicator:s} not set.')

    volume_system_type = cls._volume_system_types[type_indicator]
    return volume_system_type()

  @classmethod
  def RegisterVolumeSystem(cls, volume_system_type):
    """Registers a path specification type.

    Args:
      volume_system_type (type): path specification type.

    Raises:
      KeyError: if path specification type is already registered.
    """
    type_indicator = volume_system_type.TYPE_INDICATOR
    if type_indicator in cls._volume_system_types:
      raise KeyError(f'Volume system type: {type_indicator:s} already set.')

    cls._volume_system_types[type_indicator] = volume_system_type
