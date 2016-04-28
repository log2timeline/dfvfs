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
from dfvfs.vfs import file_entry
from dfvfs.vfs import vfs_stat


_FILE_REFERENCE_MFT_ENTRY_BITMASK = 0xffffffffffff


class NTFSAttribute(file_entry.Attribute):
  """Class that implements an attribute object using pyfsntfs."""

  def __init__(self, fsntfs_attribute):
    """Initializes the attribute object.

    Args:
      fsntfs_attribute: the NTFS attribute object (instance of
                        pyfsntfs.attribute).
    """
    super(NTFSAttribute, self).__init__()
    self._fsntfs_attribute = fsntfs_attribute

  @property
  def attribute_type(self):
    """The attribute type."""
    return self._fsntfs_attribute.attribute_type


class FileNameNTFSAttribute(NTFSAttribute):
  """Class that implements a $FILE_NAME attribute object."""

  TYPE_INDICATOR = definitions.ATTRIBUTE_TYPE_NTFS_FILE_NAME

  @property
  def access_time(self):
    """The access time (instance of Filetime)."""
    timestamp = self._fsntfs_attribute.get_access_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def creation_time(self):
    """The creation time (instance of Filetime)."""
    timestamp = self._fsntfs_attribute.get_creation_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def entry_modification_time(self):
    """The entry modification time (instance of Filetime)."""
    timestamp = self._fsntfs_attribute.get_entry_modification_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def file_attribute_flags(self):
    """The file attribute flags."""
    return self._fsntfs_attribute.file_attribute_flags

  @property
  def modification_time(self):
    """The modification time (instance of Filetime)."""
    timestamp = self._fsntfs_attribute.get_modification_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def name(self):
    """The name."""
    return self._fsntfs_attribute.name

  @property
  def parent_file_reference(self):
    """The parent file refrence."""
    return self._fsntfs_attribute.parent_file_reference


class ObjectIdentifierNTFSAttribute(NTFSAttribute):
  """Class that implements a $OBJECT_ID attribute object."""

  TYPE_INDICATOR = definitions.ATTRIBUTE_TYPE_NTFS_OBJECT_ID

  @property
  def droid_file_identifier(self):
    """The droid file identifier (an UUID string or None)."""
    return self._fsntfs_attribute.droid_file_identifier


class SecurityDescriptorNTFSAttribute(NTFSAttribute):
  """Class that implements a $SECURITY_DESCRIPTOR attribute object."""

  TYPE_INDICATOR = definitions.ATTRIBUTE_TYPE_NTFS_SECURITY_DESCRIPTOR

  @property
  def security_descriptor(self):
    """The security descriptor (instance of pyfwnt.security_descriptor)."""
    fwnt_security_descriptor = pyfwnt.security_descriptor()
    fwnt_security_descriptor.copy_from_byte_stream(self._fsntfs_attribute.data)
    return fwnt_security_descriptor


class StandardInformationNTFSAttribute(NTFSAttribute):
  """Class that implements a $STANDARD_INFORMATION attribute object."""

  TYPE_INDICATOR = definitions.ATTRIBUTE_TYPE_NTFS_STANDARD_INFORMATION

  @property
  def access_time(self):
    """The access time (instance of Filetime)."""
    timestamp = self._fsntfs_attribute.get_access_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def creation_time(self):
    """The creation time (instance of Filetime)."""
    timestamp = self._fsntfs_attribute.get_creation_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def entry_modification_time(self):
    """The entry modification time (instance of Filetime)."""
    timestamp = self._fsntfs_attribute.get_entry_modification_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def file_attribute_flags(self):
    """The file attribute flags."""
    return self._fsntfs_attribute.file_attribute_flags

  @property
  def modification_time(self):
    """The modification time (instance of Filetime)."""
    timestamp = self._fsntfs_attribute.get_modification_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def owner_identifier(self):
    """The owner identifier."""
    return self._fsntfs_attribute.owner_identifier

  @property
  def security_identifier(self):
    """The security identifier."""
    return self._fsntfs_attribute.security_identifier

  @property
  def update_sequence_number(self):
    """The update sequence number."""
    return self._fsntfs_attribute.update_sequence_number


class NTFSDataStream(file_entry.DataStream):
  """Class that implements a data stream object using pyfsntfs."""

  def __init__(self, fsntfs_data_stream):
    """Initializes the data stream object.

    Args:
      fsntfs_data_stream: the NTFS data stream object (instance of
                          pyfsntfs.data_stream).
    """
    super(NTFSDataStream, self).__init__()
    self._fsntfs_data_stream = fsntfs_data_stream

  @property
  def name(self):
    """The name."""
    if self._fsntfs_data_stream:
      return self._fsntfs_data_stream.name
    return u''


class NTFSDirectory(file_entry.Directory):
  """Class that implements a directory object using pyfsntfs."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      A path specification (instance of path.NTFSPathSpec).
    """
    # Opening a file by MFT entry is faster than opening a file by location.
    location = getattr(self.path_spec, u'location', None)
    mft_entry = getattr(self.path_spec, u'mft_entry', None)

    fsntfs_volume = self._file_system.GetNTFSVolume()
    if mft_entry is not None:
      fsntfs_file_entry = fsntfs_volume.get_file_entry(mft_entry)
    elif location is not None:
      fsntfs_file_entry = fsntfs_volume.get_file_entry_by_path(location)
    else:
      return

    for fsntfs_sub_file_entry in fsntfs_file_entry.sub_file_entries:
      directory_entry = fsntfs_sub_file_entry.name

      # Ignore references to self or parent.
      if directory_entry in [u'.', u'..']:
        continue

      file_reference = fsntfs_sub_file_entry.file_reference
      directory_entry_mft_entry = (
          file_reference & _FILE_REFERENCE_MFT_ENTRY_BITMASK)

      if location == self._file_system.PATH_SEPARATOR:
        directory_entry = self._file_system.JoinPath([directory_entry])
      else:
        directory_entry = self._file_system.JoinPath([
            location, directory_entry])

      yield ntfs_path_spec.NTFSPathSpec(
          location=directory_entry,
          mft_attribute=fsntfs_sub_file_entry.name_attribute_index,
          mft_entry=directory_entry_mft_entry, parent=self.path_spec.parent)


class NTFSFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using pyfsntfs."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_NTFS

  _ATTRIBUTE_TYPE_CLASS_MAPPINGS = {
      0x00000010: StandardInformationNTFSAttribute,
      0x00000030: FileNameNTFSAttribute,
      0x00000040: ObjectIdentifierNTFSAttribute,
      0x00000050: SecurityDescriptorNTFSAttribute,
  }

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False, fsntfs_file_entry=None):
    """Initializes the file entry object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_system: the file system object (instance of FileSystem).
      path_spec: the path specification (instance of PathSpec).
      is_root: optional boolean value to indicate if the file entry is
               the root file entry of the corresponding file system.
      is_virtual: optional boolean value to indicate if the file entry is
                  a virtual file entry emulated by the corresponding file
                  system.
      fsntfs_file_entry: optional file entry object (instance of
                         pyfsntfs.file_entry).
    """
    super(NTFSFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._fsntfs_file_entry = fsntfs_file_entry

  def _GetAttributes(self):
    """Retrieves the attributes.

    Returns:
      A list of attribute objects (instances of Attribute).

    Raises:
      BackEndError: if the pyfsntfs file entry is missing.
    """
    if self._attributes is None:
      fsntfs_file_entry = self.GetNTFSFileEntry()
      if not fsntfs_file_entry:
        raise errors.BackEndError(u'Missing pyfsntfs file entry.')

      self._attributes = []
      for fsntfs_attribute in fsntfs_file_entry.attributes:
        attribute_class = self._ATTRIBUTE_TYPE_CLASS_MAPPINGS.get(
            fsntfs_attribute.attribute_type, NTFSAttribute)

        attribute_object = attribute_class(fsntfs_attribute)
        self._attributes.append(attribute_object)

    return self._attributes

  def _GetDataStreams(self):
    """Retrieves the data streams.

    Returns:
      A list of data stream objects (instances of NTFSDataStream).

    Raises:
      BackEndError: if the pyfsntfs file entry is missing.
    """
    if self._data_streams is None:
      fsntfs_file_entry = self.GetNTFSFileEntry()
      if not fsntfs_file_entry:
        raise errors.BackEndError(u'Missing pyfsntfs file entry.')

      self._data_streams = []
      if fsntfs_file_entry.has_default_data_stream():
        self._data_streams.append(NTFSDataStream(None))

      for fsntfs_data_stream in fsntfs_file_entry.alternate_data_streams:
        self._data_streams.append(NTFSDataStream(fsntfs_data_stream))

    return self._data_streams

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      A directory object (instance of Directory) or None.

    Raises:
      BackEndError: if the pyfsntfs file entry is missing.
    """
    fsntfs_file_entry = self.GetNTFSFileEntry()
    if not fsntfs_file_entry:
      raise errors.BackEndError(u'Missing pyfsntfs file entry.')

    if fsntfs_file_entry.number_of_sub_file_entries > 0:
      return NTFSDirectory(self._file_system, self.path_spec)
    return

  def _GetLink(self):
    """Retrieves the link.

    Returns:
      A string containing the path of the linked file.

    Raises:
      BackEndError: if the pyfsntfs file entry is missing.
    """
    if self._link is None:
      fsntfs_file_entry = self.GetNTFSFileEntry()
      if not fsntfs_file_entry:
        raise errors.BackEndError(u'Missing pyfsntfs file entry.')

      self._link = u''
      if not self._IsLink(fsntfs_file_entry.file_attribute_flags):
        return self._link

      link = fsntfs_file_entry.reparse_point_print_name
      if link:
        # Strip off the drive letter, we assume the link is within
        # the same volume.
        _, _, self._link = link.rpartition(u':')

    return self._link

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of VFSStat).

    Raises:
      BackEndError: if the pyfsntfs file entry is missing.
    """
    fsntfs_file_entry = self.GetNTFSFileEntry()
    if not fsntfs_file_entry:
      raise errors.BackEndError(u'Missing pyfsntfs file entry.')

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    if fsntfs_file_entry.has_default_data_stream():
      stat_object.size = fsntfs_file_entry.get_size()

    # Date and time stat information.
    timestamp = fsntfs_file_entry.get_access_time_as_integer()
    date_time_values = dfdatetime_filetime.Filetime(timestamp=timestamp)

    stat_time, stat_time_nano = date_time_values.CopyToStatTimeTuple()
    if stat_time is not None:
      stat_object.atime = stat_time
      stat_object.atime_nano = stat_time_nano

    timestamp = fsntfs_file_entry.get_creation_time_as_integer()
    date_time_values = dfdatetime_filetime.Filetime(timestamp=timestamp)

    stat_time, stat_time_nano = date_time_values.CopyToStatTimeTuple()
    if stat_time is not None:
      stat_object.crtime = stat_time
      stat_object.crtime_nano = stat_time_nano

    timestamp = fsntfs_file_entry.get_modification_time_as_integer()
    date_time_values = dfdatetime_filetime.Filetime(timestamp=timestamp)

    stat_time, stat_time_nano = date_time_values.CopyToStatTimeTuple()
    if stat_time is not None:
      stat_object.mtime = stat_time
      stat_object.mtime_nano = stat_time_nano

    timestamp = fsntfs_file_entry.get_entry_modification_time_as_integer()
    date_time_values = dfdatetime_filetime.Filetime(timestamp=timestamp)

    stat_time, stat_time_nano = date_time_values.CopyToStatTimeTuple()
    if stat_time is not None:
      stat_object.ctime = stat_time
      stat_object.ctime_nano = stat_time_nano

    # Ownership and permissions stat information.
    # TODO: stat_object.mode
    # TODO: stat_object.uid
    # TODO: stat_object.gid

    # File entry type stat information.
    if self._IsLink(fsntfs_file_entry.file_attribute_flags):
      stat_object.type = stat_object.TYPE_LINK
    elif fsntfs_file_entry.has_directory_entries_index():
      stat_object.type = stat_object.TYPE_DIRECTORY
    else:
      stat_object.type = stat_object.TYPE_FILE

    # Other stat information.
    stat_object.ino = (
        fsntfs_file_entry.file_reference & _FILE_REFERENCE_MFT_ENTRY_BITMASK)
    stat_object.fs_type = u'NTFS'

    stat_object.is_allocated = fsntfs_file_entry.is_allocated()

    return stat_object

  def _IsLink(self, file_attribute_flags):
    """Determines if a file entry is a link.

    Args:
      file_attribute_flags: the file attribute flags.
    """
    return bool(
        file_attribute_flags & pyfsntfs.file_attribute_flags.REPARSE_POINT)

  @property
  def name(self):
    """The name of the file entry, which does not include the full path.

    Raises:
      BackEndError: if the pyfsntfs file entry is missing.
    """
    fsntfs_file_entry = self.GetNTFSFileEntry()
    if not fsntfs_file_entry:
      raise errors.BackEndError(u'Missing pyfsntfs file entry.')

    # The root directory file name is typically '.', dfVFS however uses ''.
    if self._is_root:
      return u''

    mft_attribute = getattr(self.path_spec, u'mft_attribute', None)
    if mft_attribute is not None:
      return fsntfs_file_entry.get_name_by_attribute_index(mft_attribute)
    return fsntfs_file_entry.get_name()

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of NTFSFileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield NTFSFileEntry(
            self._resolver_context, self._file_system, path_spec)

  def GetFileObject(self, data_stream_name=u''):
    """Retrieves the file-like object.

    Args:
      data_stream_name: optional data stream name. The default is
                        an empty string which represents the default
                        data stream.

    Returns:
      A file-like object (instance of FileIO) or None.

    Raises:
      BackEndError: if the pyfsntfs file entry is missing.
    """
    fsntfs_file_entry = self.GetNTFSFileEntry()
    if not fsntfs_file_entry:
      raise errors.BackEndError(u'Missing pyfsntfs file entry.')

    if not data_stream_name and not fsntfs_file_entry.has_default_data_stream():
      return

    # Make sure to make the changes on a copy of the path specification, so we
    # do not alter self.path_spec.
    path_spec = copy.deepcopy(self.path_spec)
    if data_stream_name:
      setattr(path_spec, u'data_stream', data_stream_name)

    return resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=self._resolver_context)

  def GetLinkedFileEntry(self):
    """Retrieves the linked file entry, e.g. for a symbolic link.

    Returns:
      The linked file entry (instance of NTFSFileEntry) or None.
    """
    link = self._GetLink()
    if not link:
      return

    # TODO: is there a way to determine the MFT entry here?
    link_mft_entry = None

    parent_path_spec = getattr(self.path_spec, u'parent', None)
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=link, parent=parent_path_spec)

    if (link == self._file_system.LOCATION_ROOT or
        link_mft_entry == self._file_system.MFT_ENTRY_ROOT_DIRECTORY):
      is_root = True
    else:
      is_root = False

    return NTFSFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root)

  def GetNTFSFileEntry(self):
    """Retrieves the NTFS file entry object (instance of pyfsntfs.file_entry).

    Raises:
      PathSpecError: if the path specification is missing location and
                     MFT entry.
    """
    if not self._fsntfs_file_entry:
      # Opening a file by MFT entry is faster than opening a file by location.
      # However we need the index of the corresponding $FILE_NAME MFT attribute.
      location = getattr(self.path_spec, u'location', None)
      mft_attribute = getattr(self.path_spec, u'mft_attribute', None)
      mft_entry = getattr(self.path_spec, u'mft_entry', None)

      fsntfs_volume = self._file_system.GetNTFSVolume()
      if mft_attribute is not None and mft_entry is not None:
        self._fsntfs_file_entry = fsntfs_volume.get_file_entry(mft_entry)
      elif location is not None:
        self._fsntfs_file_entry = fsntfs_volume.get_file_entry_by_path(location)
      else:
        raise errors.PathSpecError(
            u'Path specification missing location and MFT entry.')

    return self._fsntfs_file_entry

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      The parent file entry (instance of FileEntry) or None.

    Raises:
      BackEndError: if the pyfsntfs file entry is missing.
    """
    fsntfs_file_entry = self.GetNTFSFileEntry()
    if not fsntfs_file_entry:
      raise errors.BackEndError(u'Missing pyfsntfs file entry.')

    location = getattr(self.path_spec, u'location', None)
    if location is not None:
      parent_location = self._file_system.DirnamePath(location)
      if parent_location == u'':
        parent_location = self._file_system.PATH_SEPARATOR

    parent_file_reference = None
    mft_attribute = getattr(self.path_spec, u'mft_attribute', None)
    if mft_attribute is not None:
      parent_file_reference = (
          fsntfs_file_entry.get_parent_file_reference_by_attribute_index(
              mft_attribute))
    else:
      parent_file_reference = fsntfs_file_entry.get_parent_file_reference()

    if parent_file_reference is None:
      return

    parent_mft_entry = (
        parent_file_reference & _FILE_REFERENCE_MFT_ENTRY_BITMASK)

    parent_path_spec = getattr(self.path_spec, u'parent', None)
    # TODO: determine and pass the mft_attribute of the parent
    # for a faster resolve of the file entry.
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=parent_location, mft_entry=parent_mft_entry,
        parent=parent_path_spec)

    # TODO: handle parent correctly use attribute index?
    if (parent_location == self._file_system.LOCATION_ROOT or
        parent_mft_entry == self._file_system.MFT_ENTRY_ROOT_DIRECTORY):
      is_root = True
    else:
      is_root = False

    return NTFSFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root)

  def GetSecurityDescriptor(self):
    """Retrieves the security descriptor.

    Returns:
      The security descriptor (pyfwnt.security_descriptor).

    Raises:
      BackEndError: if the pyfsntfs file entry is missing.
    """
    fsntfs_file_entry = self.GetNTFSFileEntry()
    if not fsntfs_file_entry:
      raise errors.BackEndError(u'Missing pyfsntfs file entry.')

    fwnt_security_descriptor = pyfwnt.security_descriptor()
    fwnt_security_descriptor.copy_from_byte_stream(
        fsntfs_file_entry.security_descriptor_data)

    return fwnt_security_descriptor
