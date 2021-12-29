# -*- coding: utf-8 -*-
"""The NTFS attribute implementations."""

import pyfwnt

from dfdatetime import filetime as dfdatetime_filetime

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.vfs import attribute


class NTFSAttribute(attribute.Attribute):
  """File system attribute that uses pyfsntfs."""

  def __init__(self, fsntfs_attribute):
    """Initializes an attribute.

    Args:
      fsntfs_attribute (pyfsntfs.attribute): NTFS attribute.

    Raises:
      BackEndError: if the pyfsntfs attribute is missing.
    """
    if not fsntfs_attribute:
      raise errors.BackEndError('Missing pyfsntfs attribute.')

    super(NTFSAttribute, self).__init__()
    self._fsntfs_attribute = fsntfs_attribute

  @property
  def attribute_type(self):
    """The attribute type."""
    return self._fsntfs_attribute.attribute_type


class FileNameNTFSAttribute(NTFSAttribute):
  """NTFS $FILE_NAME file system attribute."""

  TYPE_INDICATOR = definitions.ATTRIBUTE_TYPE_NTFS_FILE_NAME

  @property
  def access_time(self):
    """dfdatetime.Filetime: access time or None if not set."""
    timestamp = self._fsntfs_attribute.get_access_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def creation_time(self):
    """dfdatetime.Filetime: creation time or None if not set."""
    timestamp = self._fsntfs_attribute.get_creation_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def entry_modification_time(self):
    """dfdatetime.Filetime: entry modification time or None if not set."""
    timestamp = self._fsntfs_attribute.get_entry_modification_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def file_attribute_flags(self):
    """int: file attribute flags or None if not available."""
    return self._fsntfs_attribute.file_attribute_flags

  @property
  def modification_time(self):
    """dfdatetime.Filetime: modification time."""
    timestamp = self._fsntfs_attribute.get_modification_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def name(self):
    """str: name."""
    return self._fsntfs_attribute.name

  @property
  def name_space(self):
    """int: name_space."""
    return self._fsntfs_attribute.name_space

  @property
  def parent_file_reference(self):
    """int: parent file reference."""
    return self._fsntfs_attribute.parent_file_reference


class ObjectIdentifierNTFSAttribute(NTFSAttribute):
  """NTFS $OBJECT_ID file system attribute."""

  TYPE_INDICATOR = definitions.ATTRIBUTE_TYPE_NTFS_OBJECT_ID

  @property
  def droid_file_identifier(self):
    """str: droid file identifier, formatted as an UUID."""
    return self._fsntfs_attribute.droid_file_identifier


class SecurityDescriptorNTFSAttribute(NTFSAttribute):
  """NTFS $SECURITY_DESCRIPTOR file system attribute."""

  TYPE_INDICATOR = definitions.ATTRIBUTE_TYPE_NTFS_SECURITY_DESCRIPTOR

  @property
  def security_descriptor(self):
    """pyfwnt.security_descriptor: security descriptor."""
    fwnt_security_descriptor = pyfwnt.security_descriptor()
    fwnt_security_descriptor.copy_from_byte_stream(self._fsntfs_attribute.data)
    return fwnt_security_descriptor


class StandardInformationNTFSAttribute(NTFSAttribute):
  """NTFS $STANDARD_INFORMATION file system attribute."""

  TYPE_INDICATOR = definitions.ATTRIBUTE_TYPE_NTFS_STANDARD_INFORMATION

  @property
  def access_time(self):
    """dfdatetime.Filetime: access time or None if not set."""
    timestamp = self._fsntfs_attribute.get_access_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def creation_time(self):
    """dfdatetime.Filetime: creation time or None if not set."""
    timestamp = self._fsntfs_attribute.get_creation_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def entry_modification_time(self):
    """dfdatetime.Filetime: entry modification time or None if not set."""
    timestamp = self._fsntfs_attribute.get_entry_modification_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def file_attribute_flags(self):
    """int: file attribute flags or None if not available."""
    return self._fsntfs_attribute.file_attribute_flags

  @property
  def modification_time(self):
    """dfdatetime.Filetime: modification time or None if not set."""
    timestamp = self._fsntfs_attribute.get_modification_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def owner_identifier(self):
    """int: owner identifier."""
    return self._fsntfs_attribute.owner_identifier

  @property
  def security_descriptor_identifier(self):
    """int: security descriptor identifier."""
    return self._fsntfs_attribute.security_descriptor_identifier

  @property
  def update_sequence_number(self):
    """int: update sequence number."""
    return self._fsntfs_attribute.update_sequence_number
