# -*- coding: utf-8 -*-
"""The NTFS file entry implementation."""

import copy

import pyfsntfs
import pyfwnt

from dfdatetime import filetime as dfdatetime_filetime

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import ntfs_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import attribute
from dfvfs.vfs import extent
from dfvfs.vfs import file_entry
from dfvfs.vfs import ntfs_attribute
from dfvfs.vfs import ntfs_data_stream
from dfvfs.vfs import ntfs_directory


class NTFSFileEntry(file_entry.FileEntry):
  """File system file entry that uses pyfsntfs."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_NTFS

  _ATTRIBUTE_TYPE_CLASS_MAPPINGS = {
      0x00000010: ntfs_attribute.StandardInformationNTFSAttribute,
      0x00000030: ntfs_attribute.FileNameNTFSAttribute,
      0x00000040: ntfs_attribute.ObjectIdentifierNTFSAttribute,
      0x00000050: ntfs_attribute.SecurityDescriptorNTFSAttribute,
  }

  _FILE_REFERENCE_MFT_ENTRY_BITMASK = 0xffffffffffff

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

    file_attribute_flags = fsntfs_file_entry.file_attribute_flags
    if self._IsLink(file_attribute_flags):
      self.entry_type = definitions.FILE_ENTRY_TYPE_LINK
    elif fsntfs_file_entry.has_directory_entries_index():
      self.entry_type = definitions.FILE_ENTRY_TYPE_DIRECTORY
    elif self._IsDevice(file_attribute_flags):
      self.entry_type = definitions.FILE_ENTRY_TYPE_DEVICE
    else:
      self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  def _GetAttributes(self):
    """Retrieves the attributes.

    Returns:
      list[Attribute]: attributes.
    """
    if self._attributes is None:
      self._attributes = []

      for fsntfs_attribute in self._fsntfs_file_entry.attributes:
        attribute_class = self._ATTRIBUTE_TYPE_CLASS_MAPPINGS.get(
            fsntfs_attribute.attribute_type, ntfs_attribute.NTFSAttribute)

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
        data_stream = ntfs_data_stream.NTFSDataStream(self, None)
        self._data_streams.append(data_stream)

      for fsntfs_data_stream in self._fsntfs_file_entry.alternate_data_streams:
        data_stream = ntfs_data_stream.NTFSDataStream(self, fsntfs_data_stream)
        self._data_streams.append(data_stream)

    return self._data_streams

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      NTFSDirectory: a directory.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return ntfs_directory.NTFSDirectory(
        self._file_system, self.path_spec, self._fsntfs_file_entry)

  def _GetLink(self):
    """Retrieves the link.

    Returns:
      str: path of the linked file.
    """
    if self._link is None:
      self._link = self._fsntfs_file_entry.symbolic_link_target
      if self._link:
        # Strip off the drive letter, we assume the link is within
        # the same volume.
        _, _, self._link = self._link.rpartition(':')

    return self._link

  def _GetStatAttribute(self):
    """Retrieves a stat attribute.

    Returns:
      StatAttribute: a stat attribute or None if not available.
    """
    stat_attribute = attribute.StatAttribute()
    stat_attribute.inode_number = getattr(
        self._fsntfs_file_entry, 'file_reference', None)
    stat_attribute.number_of_links = getattr(
        self._fsntfs_file_entry, 'number_of_links', None)
    stat_attribute.size = getattr(self._fsntfs_file_entry, 'size', None)
    stat_attribute.type = self.entry_type

    return stat_attribute

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      NTFSFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield NTFSFileEntry(
            self._resolver_context, self._file_system, path_spec)

  def _IsDevice(self, file_attribute_flags):
    """Determines if a file entry is a device.

    Args:
      file_attribute_flags (int): file attribute flags.

    Returns:
      bool: True if a file entry is device link, false otherwise.
    """
    if file_attribute_flags is None:
      return False
    return bool(file_attribute_flags & pyfsntfs.file_attribute_flags.DEVICE)

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
    return getattr(self._fsntfs_file_entry, 'size', None)

  def GetExtents(self):
    """Retrieves the extents.

    Returns:
      list[Extent]: the extents.
    """
    extents = []
    for extent_index in range(self._fsntfs_file_entry.number_of_extents):
      extent_offset, extent_size, extent_flags = (
          self._fsntfs_file_entry.get_extent(extent_index))

      if extent_flags & 0x1:
        extent_type = definitions.EXTENT_TYPE_SPARSE
      else:
        extent_type = definitions.EXTENT_TYPE_DATA

      data_stream_extent = extent.Extent(
          extent_type=extent_type, offset=extent_offset, size=extent_size)
      extents.append(data_stream_extent)

    return extents

  def GetFileObject(self, data_stream_name=''):
    """Retrieves a file-like object of a specific data stream.

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
        parent_file_reference & self._FILE_REFERENCE_MFT_ENTRY_BITMASK)

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
