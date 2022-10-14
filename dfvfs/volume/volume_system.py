# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) volume system interface."""

import abc

from dfvfs.lib import errors
from dfvfs.resolver import resolver


class VolumeAttribute(object):
  """The VFS volume attribute."""

  def __init__(self, identifier, value):
    """Initializes the volume attribute object.

    Args:
      identifier (str): identifier of the attribute within the volume.
      value (object): value of the attribute.
    """
    super(VolumeAttribute, self).__init__()
    self.identifier = identifier
    self.value = value


class VolumeExtent(object):
  """The VFS volume extent."""

  EXTENT_TYPE_DATA = 0
  EXTENT_TYPE_SPARSE = 1

  def __init__(self, offset, size, extent_type=EXTENT_TYPE_DATA):
    """Initializes a volume extent.

    Args:
      offset (int): start offset of the extent, in bytes.
      size (int): size of the extent, in bytes.
      extent_type (Optional[str]): type of extent.
    """
    super(VolumeExtent, self).__init__()
    self.offset = offset
    self.size = size
    self.extent_type = extent_type


class Volume(object):
  """The VFS volume interface."""

  def __init__(self, identifier):
    """Initializes a volume.

    Args:
      identifier (str): identifier of the attribute within the volume.
    """
    super(Volume, self).__init__()
    self.identifier = identifier
    self._attributes = {}
    self._extents = []
    self._is_parsed = False

  def _AddAttribute(self, attribute):
    """Adds an attribute.

    Args:
      attribute (VolumeAttribute): a volume attribute.

    Raises:
      KeyError: if volume attribute is already set for the corresponding volume
          attribute identifier.
    """
    if attribute.identifier in self._attributes:
      raise KeyError((
          f'Volume attribute object already set for volume attribute '
          f'identifier: {attribute.identifier:s}.'))

    self._attributes[attribute.identifier] = attribute

  @abc.abstractmethod
  def _Parse(self):
    """Extracts attributes and extents from the volume."""

  @property
  def attributes(self):
    """generator[VolumeAttribute]: volume attributes generator."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return iter(self._attributes.values())

  @property
  def extents(self):
    """list[VolumeExtent]: volume extents."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return self._extents

  @property
  def number_of_attributes(self):
    """int: number of attributes."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return len(self._attributes)

  @property
  def number_of_extents(self):
    """int: number of extents."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return len(self._extents)

  def GetAttribute(self, identifier):
    """Retrieves a specific attribute.

    Args:
      identifier (str): identifier of the attribute within the volume.

    Returns:
      VolumeAttribute: volume attribute or None if not available.
    """
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    if identifier not in self._attributes:
      return None

    return self._attributes[identifier]

  def HasExternalData(self):
    """Determines if the volume has external stored data.

    Returns:
      bool: True if the volume has external stored data.
    """
    return False


class VolumeSystem(object):
  """The VFS volume system interface."""

  TYPE_INDICATOR = None

  VOLUME_IDENTIFIER_PREFIX = 'v'

  def __init__(self):
    """Initializes a volume system."""
    super(VolumeSystem, self).__init__()
    self._file_system = None
    self._is_parsed = False
    self._sections = []
    self._volumes = {}
    self._volume_identifiers = []

  def _AddVolume(self, volume):
    """Adds a volume.

    Args:
      volume (Volume): a volume.

    Raises:
      KeyError: if volume is already set for the corresponding volume
          identifier.
    """
    if volume.identifier in self._volumes:
      raise KeyError((
          f'Volume object already set for volume identifier: '
          f'{volume.identifier:s}'))

    self._volumes[volume.identifier] = volume
    self._volume_identifiers.append(volume.identifier)

  @abc.abstractmethod
  def _Parse(self):
    """Extracts sections and volumes from the volume system."""

  @property
  def number_of_sections(self):
    """int: number of sections."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return len(self._sections)

  @property
  def number_of_volumes(self):
    """int: number of volumes."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return len(self._volumes)

  @property
  def sections(self):
    """list[VolumeExtent]: sections."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return self._sections

  @property
  def volume_identifiers(self):
    """list[str]: volume identifiers."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return list(self._volume_identifiers)

  @property
  def volumes(self):
    """generator(Volume): volumes generator."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return iter(self._volumes.values())

  def GetSectionByIndex(self, section_index):
    """Retrieves a specific section based on the index.

    Args:
      section_index (int): index of the section.

    Returns:
      VolumeExtent: a volume extent or None if not available.
    """
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    if section_index < 0 or section_index >= len(self._sections):
      return None

    return self._sections[section_index]

  def GetVolumeByIdentifier(self, volume_identifier):
    """Retrieves a specific volume based on the identifier.

    Args:
      volume_identifier (str): identifier of the volume within
          the volume system.

    Returns:
      Volume: a volume.
    """
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return self._volumes[volume_identifier]

  def GetVolumeByIndex(self, volume_index):
    """Retrieves a specific volume based on the index.

    Args:
      volume_index (int): index of the volume.

    Returns:
      Volume: a volume or None if not available.
    """
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    if volume_index < 0 or volume_index >= len(self._volume_identifiers):
      return None

    volume_identifier = self._volume_identifiers[volume_index]
    return self._volumes[volume_identifier]

  def Open(self, path_spec):
    """Opens a volume defined by path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Raises:
      VolumeSystemError: if the virtual file system representing the volume
          system could not be resolved.
    """
    self._file_system = resolver.Resolver.OpenFileSystem(path_spec)
    if self._file_system is None:
      raise errors.VolumeSystemError('Unable to resolve path specification.')

    if self._file_system.type_indicator != self.TYPE_INDICATOR:
      raise errors.VolumeSystemError('Unsupported type indicator.')
