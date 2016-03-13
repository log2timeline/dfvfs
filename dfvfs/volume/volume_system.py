# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) volume system interface."""

import abc


class VolumeAttribute(object):
  """The VFS volume attribute object."""

  def __init__(self, identifier, value):
    """Initializes the volume attribute object.

    Args:
      identifier: string that uniquely identifies the attribute within the
                  volume.
      value: the value of the attribute.
    """
    super(VolumeAttribute, self).__init__()
    self.identifier = identifier
    self.value = value


class VolumeExtent(object):
  """The VFS volume extent object."""

  EXTENT_TYPE_DATA = 0
  EXTENT_TYPE_SPARSE = 1

  def __init__(self, offset, size, extent_type=EXTENT_TYPE_DATA):
    """Initializes the volume extent object.

    Args:
      offset: the start offset of the extent, in bytes.
      size: the size of the extent, in bytes.
      extent_type: optional type of extent, the default is
                   EXTENT_TYPE_DATA.
    """
    super(VolumeExtent, self).__init__()
    self.offset = offset
    self.size = size
    self.extent_type = extent_type


class Volume(object):
  """The VFS volume interface."""

  def __init__(self, identifier):
    """Initializes the volume extent object.

    Args:
      identifier: string that uniquely identifies the volume within the volume
                  system.
    """
    super(Volume, self).__init__()
    self.identifier = identifier
    self._attributes = {}
    self._extents = []
    self._is_parsed = False

  def _AddAttribute(self, attribute):
    """Adds an attribute.

    Args:
      attribute: the volume attribute object (instance of VolumeAttribute).

    Raises:
      KeyError: if volume attribute is already set for the corresponding volume
                attribute identifier.
    """
    if attribute.identifier in self._attributes:
      raise KeyError((
          u'Volume attribute object already set for volume attribute '
          u'identifier: {0:s}.').format(attribute.identifier))

    self._attributes[attribute.identifier] = attribute

  @abc.abstractmethod
  def _Parse(self):
    """Extracts attributes and extents from the volume."""

  @property
  def attributes(self):
    """The attributes."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return iter(self._attributes.values())

  @property
  def extents(self):
    """The extents."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return self._extents

  @property
  def number_of_attributes(self):
    """The number of attributes."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return len(self._attributes)

  @property
  def number_of_extents(self):
    """The number of extents."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return len(self._extents)

  def GetAttribute(self, identifier):
    """Retrieves a specific attribute.

    Args:
      identifier: the attribute identifier.

    Returns:
      The volume attribute object (instance of VolumeAttribute) or None.
    """
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    if identifier not in self._attributes:
      return

    return self._attributes[identifier]

  def HasExternalData(self):
    """Determines if the volume has external stored data.

    Returns:
      A boolean to indicate the volume has external stored data.
    """
    return False


class VolumeSystem(object):
  """The VFS volume system interface."""

  def __init__(self):
    """Initializes the volume system object."""
    super(VolumeSystem, self).__init__()
    self._is_parsed = False
    self._sections = []
    self._volumes = {}
    self._volume_identifiers = []

  def _AddVolume(self, volume):
    """Adds a volume.

    Args:
      volume: the volume object (instance of Volume).

    Raises:
      KeyError: if volume is already set for the corresponding volume
                identifier.
    """
    if volume.identifier in self._volumes:
      raise KeyError(
          u'Volume object already set for volume identifier: {0:s}'.format(
              volume.identifier))

    self._volumes[volume.identifier] = volume
    self._volume_identifiers.append(volume.identifier)

  @abc.abstractmethod
  def _Parse(self):
    """Extracts sections and volumes from the volume system."""

  @property
  def number_of_sections(self):
    """The number of sections."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return len(self._sections)

  @property
  def number_of_volumes(self):
    """The number of volumes."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return len(self._volumes)

  @property
  def sections(self):
    """The sections."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return self._sections

  @property
  def volumes(self):
    """The volumes."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return iter(self._volumes.values())

  def GetSectionByIndex(self, section_index):
    """Retrieves a specific section based on the index.

    Args:
      section_index: the index of the section.
    """
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    if section_index < 0 or section_index >= len(self._sections):
      return
    return self._sections[section_index]

  def GetVolumeByIdentifier(self, volume_identifier):
    """Retrieves a specific volume based on the identifier.

    Args:
      volume_identifier: string that uniquely identifies the volume within the
                         volume system.

    Returns:
      The volume object (instance of Volume).
    """
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return self._volumes[volume_identifier]

  def GetVolumeByIndex(self, volume_index):
    """Retrieves a specific volume based on the index.

    Args:
      volume_index: the index of the volume.

    Returns:
      The volume object (instance of Volume).
    """
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    if volume_index < 0 or volume_index >= len(self._volume_identifiers):
      return
    volume_identifier = self._volume_identifiers[volume_index]
    return self._volumes[volume_identifier]

  @abc.abstractmethod
  def Open(self, path_spec):
    """Opens a volume object defined by path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).
    """
