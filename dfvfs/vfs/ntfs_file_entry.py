# -*- coding: utf-8 -*-
"""The NTFS file entry implementation."""

from __future__ import unicode_literals

import copy

import pyfsntfs
import pyfwnt

from dfdatetime import filetime as dfdatetime_filetime

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import ntfs_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_entry


_FILE_REFERENCE_MFT_ENTRY_BITMASK = 0xffffffffffff


class NTFSAttribute(file_entry.Attribute):
  """File system attribute that uses pyfsntfs."""

  def __init__(self, fsntfs_attribute):
    """Initializes the attribute object.

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


class NTFSDataStream(file_entry.DataStream):
  """File system data stream that uses pyfsntfs."""

  def __init__(self, fsntfs_data_stream):
    """Initializes the data stream object.

    Args:
      fsntfs_data_stream (pyfsntfs.data_stream): NTFS data stream.
    """
    super(NTFSDataStream, self).__init__()
    self._fsntfs_data_stream = fsntfs_data_stream

  @property
  def name(self):
    """str: name."""
    return getattr(self._fsntfs_data_stream, 'name', '')

  def IsDefault(self):
    """Determines if the data stream is the default data stream.

    Returns:
      bool: True if the data stream is the default data stream.
    """
    return not self._fsntfs_data_stream


class NTFSDirectory(file_entry.Directory):
  """File system directory that uses pyfsntfs."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      NTFSPathSpec: NTFS path specification.
    """
    try:
      fsntfs_file_entry = self._file_system.GetNTFSFileEntryByPathSpec(
          self.path_spec)
    except errors.PathSpecError:
      fsntfs_file_entry = None

    if fsntfs_file_entry:
      location = getattr(self.path_spec, 'location', None)

      for fsntfs_sub_file_entry in fsntfs_file_entry.sub_file_entries:
        directory_entry = fsntfs_sub_file_entry.name

        # Ignore references to self or parent.
        if directory_entry in ('.', '..'):
          continue

        file_reference = fsntfs_sub_file_entry.file_reference
        directory_entry_mft_entry = (
            file_reference & _FILE_REFERENCE_MFT_ENTRY_BITMASK)

        if not location or location == self._file_system.PATH_SEPARATOR:
          directory_entry = self._file_system.JoinPath([directory_entry])
        else:
          directory_entry = self._file_system.JoinPath([
              location, directory_entry])

        yield ntfs_path_spec.NTFSPathSpec(
            location=directory_entry,
            mft_attribute=fsntfs_sub_file_entry.name_attribute_index,
            mft_entry=directory_entry_mft_entry, parent=self.path_spec.parent)


class NTFSFileEntry(file_entry.FileEntry):
  """File system file entry that uses pyfsntfs."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_NTFS

  _ATTRIBUTE_TYPE_CLASS_MAPPINGS = {
      0x00000010: StandardInformationNTFSAttribute,
      0x00000030: FileNameNTFSAttribute,
      0x00000040: ObjectIdentifierNTFSAttribute,
      0x00000050: SecurityDescriptorNTFSAttribute,
  }

  def __init__(
      self, resolver_context, file_system, path_spec, fsntfs_file_entry=None,
      is_root=False, is_virtual=False):
    """Initializes the file entry object.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      fsntfs_file_entry (Optional[pyfsntfs.file_entry]): NTFS file entry.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
          entry emulated by the corresponding file system.

    Raises:
      BackEndError: if the pyfsntfs file entry is missing.
    """
    if not fsntfs_file_entry:
      fsntfs_file_entry = file_system.GetNTFSFileEntryByPathSpec(path_spec)
    if not fsntfs_file_entry:
      raise errors.BackEndError('Missing pyfsntfs file entry.')

    super(NTFSFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._fsntfs_file_entry = fsntfs_file_entry

    if self._IsLink(fsntfs_file_entry.file_attribute_flags):
      self.entry_type = definitions.FILE_ENTRY_TYPE_LINK
    elif fsntfs_file_entry.has_directory_entries_index():
      self.entry_type = definitions.FILE_ENTRY_TYPE_DIRECTORY
    else:
      self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  def _GetAttributes(self):
    """Retrieves the attributes.

    Returns:
      list[NTFSAttribute]: attributes.
    """
    if self._attributes is None:
      self._attributes = []
      for fsntfs_attribute in self._fsntfs_file_entry.attributes:
        attribute_class = self._ATTRIBUTE_TYPE_CLASS_MAPPINGS.get(
            fsntfs_attribute.attribute_type, NTFSAttribute)

        attribute_object = attribute_class(fsntfs_attribute)
        self._attributes.append(attribute_object)

    return self._attributes

  def _GetDataStreams(self):
    """Retrieves the data streams.

    Returns:
      list[NTFSDataStream]: data streams.
    """
    if self._data_streams is None:
      self._data_streams = []
      if self._fsntfs_file_entry.has_default_data_stream():
        data_stream = NTFSDataStream(None)
        self._data_streams.append(data_stream)

      for fsntfs_data_stream in self._fsntfs_file_entry.alternate_data_streams:
        data_stream = NTFSDataStream(fsntfs_data_stream)
        self._data_streams.append(data_stream)

    return self._data_streams

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      NTFSDirectory: a directory.
    """
    if self._directory is None:
      self._directory = NTFSDirectory(self._file_system, self.path_spec)

    return self._directory

  def _GetLink(self):
    """Retrieves the link.

    Returns:
      str: path of the linked file.
    """
    if self._link is None:
      self._link = self._fsntfs_file_entry.reparse_point_print_name
      if self._link:
        # Strip off the drive letter, we assume the link is within
        # the same volume.
        _, _, self._link = self._link.rpartition(':')

    return self._link

  def _GetStat(self):
    """Retrieves information about the file entry.

    Returns:
      VFSStat: a stat object.
    """
    stat_object = super(NTFSFileEntry, self)._GetStat()

    # Other stat information.
    file_reference = self._fsntfs_file_entry.file_reference
    stat_object.ino = file_reference & _FILE_REFERENCE_MFT_ENTRY_BITMASK
    stat_object.fs_type = 'NTFS'

    return stat_object

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      NTFSFileEntry: a sub file entry.
    """
    if self.entry_type == definitions.FILE_ENTRY_TYPE_DIRECTORY:
      directory = self._GetDirectory()
      for path_spec in directory.entries:
        yield NTFSFileEntry(
            self._resolver_context, self._file_system, path_spec)

  def _IsLink(self, file_attribute_flags):
    """Determines if a file entry is a link.

    Args:
      file_attribute_flags (int): file attribute flags.

    Returns:
      bool: True if a file entry is a link, false otherwise.
    """
    if file_attribute_flags is None:
      return False
    return bool(
        file_attribute_flags & pyfsntfs.file_attribute_flags.REPARSE_POINT)

  @property
  def access_time(self):
    """dfdatetime.DateTimeValues: access time or None if not available."""
    timestamp = self._fsntfs_file_entry.get_access_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def change_time(self):
    """dfdatetime.DateTimeValues: change time or None if not available."""
    timestamp = self._fsntfs_file_entry.get_entry_modification_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def creation_time(self):
    """dfdatetime.DateTimeValues: creation time or None if not available."""
    timestamp = self._fsntfs_file_entry.get_creation_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def modification_time(self):
    """dfdatetime.DateTimeValues: modification time or None if not available."""
    timestamp = self._fsntfs_file_entry.get_modification_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def name(self):
    """str: name of the file entry, which does not include the full path."""
    # The root directory file name is typically '.', dfVFS however uses ''.
    if self._is_root:
      return ''

    mft_attribute = getattr(self.path_spec, 'mft_attribute', None)
    if mft_attribute is not None:
      return self._fsntfs_file_entry.get_name_by_attribute_index(mft_attribute)

    return self._fsntfs_file_entry.get_name()

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    return self._fsntfs_file_entry.get_size()

  def GetFileObject(self, data_stream_name=''):
    """Retrieves the file-like object.

    Args:
      data_stream_name (Optional[str]): data stream name, where an empty
          string represents the default data stream.

    Returns:
      NTFSFileIO: file-like object or None.
    """
    if (not data_stream_name and
        not self._fsntfs_file_entry.has_default_data_stream()):
      return None

    # Make sure to make the changes on a copy of the path specification, so we
    # do not alter self.path_spec.
    path_spec = copy.deepcopy(self.path_spec)
    if data_stream_name:
      setattr(path_spec, 'data_stream', data_stream_name)

    return resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=self._resolver_context)

  def GetLinkedFileEntry(self):
    """Retrieves the linked file entry, e.g. for a symbolic link.

    Returns:
      NTFSFileEntry: linked file entry or None.
    """
    link = self._GetLink()
    if not link:
      return None

    # TODO: is there a way to determine the MFT entry here?
    link_mft_entry = None

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=link, parent=parent_path_spec)

    is_root = bool(
        link == self._file_system.LOCATION_ROOT or
        link_mft_entry == self._file_system.MFT_ENTRY_ROOT_DIRECTORY)

    return NTFSFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root)

  def GetNTFSFileEntry(self):
    """Retrieves the NTFS file entry.

    Returns:
      pyfsntfs.file_entry: NTFS file entry.
    """
    return self._fsntfs_file_entry

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      NTFSFileEntry: parent file entry or None if not available.
    """
    location = getattr(self.path_spec, 'location', None)
    if location is not None:
      parent_location = self._file_system.DirnamePath(location)
      if parent_location == '':
        parent_location = self._file_system.PATH_SEPARATOR

    parent_file_reference = None
    mft_attribute = getattr(self.path_spec, 'mft_attribute', None)
    if mft_attribute is not None:
      parent_file_reference = (
          self._fsntfs_file_entry.get_parent_file_reference_by_attribute_index(
              mft_attribute))
    else:
      parent_file_reference = (
          self._fsntfs_file_entry.get_parent_file_reference())

    if parent_file_reference is None:
      return None

    parent_mft_entry = (
        parent_file_reference & _FILE_REFERENCE_MFT_ENTRY_BITMASK)

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    # TODO: determine and pass the mft_attribute of the parent
    # for a faster resolve of the file entry.
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=parent_location, mft_entry=parent_mft_entry,
        parent=parent_path_spec)

    # TODO: handle parent correctly use attribute index?
    is_root = bool(
        parent_location == self._file_system.LOCATION_ROOT or
        parent_mft_entry == self._file_system.MFT_ENTRY_ROOT_DIRECTORY)

    return NTFSFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root)

  def GetSecurityDescriptor(self):
    """Retrieves the security descriptor.

    Returns:
      pyfwnt.security_descriptor: security descriptor.
    """
    fwnt_security_descriptor = pyfwnt.security_descriptor()
    fwnt_security_descriptor.copy_from_byte_stream(
        self._fsntfs_file_entry.security_descriptor_data)

    return fwnt_security_descriptor

  def IsAllocated(self):
    """Determines if the file entry is allocated.

    Returns:
      bool: True if the file entry is allocated.
    """
    return self._fsntfs_file_entry.is_allocated()
