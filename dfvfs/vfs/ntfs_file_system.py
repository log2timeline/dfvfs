# -*- coding: utf-8 -*-
"""The NTFS file system implementation."""

import pyfsntfs

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import ntfs_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system
from dfvfs.vfs import ntfs_file_entry


class NTFSFileSystem(file_system.FileSystem):
  """File system that uses pyfsntfs."""

  MFT_ENTRY_ROOT_DIRECTORY = 5

  LOCATION_ROOT = '\\'
  PATH_SEPARATOR = '\\'

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_NTFS

  def __init__(self, resolver_context, path_spec):
    """Initializes a file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(NTFSFileSystem, self).__init__(resolver_context, path_spec)
    self._file_object = None
    self._fsntfs_volume = None

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._fsntfs_volume = None
    self._file_object = None

  def _Open(self, mode='rb'):
    """Opens the file system object defined by path specification.

    Args:
      mode (Optional[str]): file access mode. The default is 'rb' which
          represents read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not self._path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    file_object = resolver.Resolver.OpenFileObject(
        self._path_spec.parent, resolver_context=self._resolver_context)

    fsntfs_volume = pyfsntfs.volume()
    fsntfs_volume.open_file_object(file_object)

    self._file_object = file_object
    self._fsntfs_volume = fsntfs_volume

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if the file entry exists.

    Raises:
      BackEndError: if the file entry cannot be opened.
    """
    # Opening a file by MFT entry is faster than opening a file by location.
    # However we need the index of the corresponding $FILE_NAME MFT attribute.
    fsntfs_file_entry = None
    location = getattr(path_spec, 'location', None)
    mft_attribute = getattr(path_spec, 'mft_attribute', None)
    mft_entry = getattr(path_spec, 'mft_entry', None)

    try:
      if mft_attribute is not None and mft_entry is not None:
        fsntfs_file_entry = self._fsntfs_volume.get_file_entry(mft_entry)
      elif location is not None:
        fsntfs_file_entry = self._fsntfs_volume.get_file_entry_by_path(location)

    except IOError as exception:
      raise errors.BackEndError(exception)

    return fsntfs_file_entry is not None

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      NTFSFileEntry: file entry or None if not available.

    Raises:
      BackEndError: if the file entry cannot be opened.
    """
    # Opening a file by MFT entry is faster than opening a file by location.
    # However we need the index of the corresponding $FILE_NAME MFT attribute.
    fsntfs_file_entry = None
    location = getattr(path_spec, 'location', None)
    mft_attribute = getattr(path_spec, 'mft_attribute', None)
    mft_entry = getattr(path_spec, 'mft_entry', None)

    if (location == self.LOCATION_ROOT or
        mft_entry == self.MFT_ENTRY_ROOT_DIRECTORY):
      fsntfs_file_entry = self._fsntfs_volume.get_root_directory()
      return ntfs_file_entry.NTFSFileEntry(
          self._resolver_context, self, path_spec,
          fsntfs_file_entry=fsntfs_file_entry, is_root=True)

    try:
      if mft_attribute is not None and mft_entry is not None:
        fsntfs_file_entry = self._fsntfs_volume.get_file_entry(mft_entry)
      elif location is not None:
        fsntfs_file_entry = self._fsntfs_volume.get_file_entry_by_path(location)

    except IOError as exception:
      raise errors.BackEndError(exception)

    if fsntfs_file_entry is None:
      return None

    return ntfs_file_entry.NTFSFileEntry(
        self._resolver_context, self, path_spec,
        fsntfs_file_entry=fsntfs_file_entry)

  def GetNTFSFileEntryByPathSpec(self, path_spec):
    """Retrieves the NTFS file entry for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      pyfsntfs.file_entry: NTFS file entry.

    Raises:
      PathSpecError: if the path specification is missing location and
          MFT entry.
    """
    # Opening a file by MFT entry is faster than opening a file by location.
    # However we need the index of the corresponding $FILE_NAME MFT attribute.
    location = getattr(path_spec, 'location', None)
    mft_attribute = getattr(path_spec, 'mft_attribute', None)
    mft_entry = getattr(path_spec, 'mft_entry', None)

    if mft_attribute is not None and mft_entry is not None:
      fsntfs_file_entry = self._fsntfs_volume.get_file_entry(mft_entry)
    elif location is not None:
      fsntfs_file_entry = self._fsntfs_volume.get_file_entry_by_path(location)
    else:
      raise errors.PathSpecError(
          'Path specification missing location and MFT entry.')

    return fsntfs_file_entry

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      NTFSFileEntry: file entry.
    """
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=self.LOCATION_ROOT, mft_entry=self.MFT_ENTRY_ROOT_DIRECTORY,
        parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
