# -*- coding: utf-8 -*-
"""The NTFS file system implementation."""

import pyfsntfs

# This is necessary to prevent a circular import.
import dfvfs.vfs.ntfs_file_entry

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import ntfs_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system


class NTFSFileSystem(file_system.FileSystem):
  """Class that implements a file system object using pyfsntfs."""

  MFT_ENTRY_ROOT_DIRECTORY = 5

  LOCATION_ROOT = u'\\'
  PATH_SEPARATOR = u'\\'

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_NTFS

  def __init__(self, resolver_context):
    """Initializes a file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(NTFSFileSystem, self).__init__(resolver_context)
    self._file_object = None
    self._fsntfs_volume = None

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._fsntfs_volume = None

    self._file_object.close()
    self._file_object = None

  def _Open(self, path_spec, mode='rb'):
    """Opens the file system object defined by path specification.

    Args:
      path_spec: a path specification (instance of PathSpec).
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification without parent.')

    try:
      file_object = resolver.Resolver.OpenFileObject(
          path_spec.parent, resolver_context=self._resolver_context)
      fsnfts_volume = pyfsntfs.volume()
      fsnfts_volume.open_file_object(file_object)
    except:
      file_object.close()
      raise

    self._file_object = file_object
    self._fsntfs_volume = fsnfts_volume

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      Boolean indicating if the file entry exists.

    Raises:
      BackEndError: if the file entry cannot be opened.
    """
    # Opening a file by MFT entry is faster than opening a file by location.
    # However we need the index of the corresponding $FILE_NAME MFT attribute.
    fsntfs_file_entry = None
    location = getattr(path_spec, u'location', None)
    mft_attribute = getattr(path_spec, u'mft_attribute', None)
    mft_entry = getattr(path_spec, u'mft_entry', None)

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
      path_spec: a path specification (instance of PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry) or None.

    Raises:
      BackEndError: if the file entry cannot be opened.
    """
    # Opening a file by MFT entry is faster than opening a file by location.
    # However we need the index of the corresponding $FILE_NAME MFT attribute.
    fsntfs_file_entry = None
    location = getattr(path_spec, u'location', None)
    mft_attribute = getattr(path_spec, u'mft_attribute', None)
    mft_entry = getattr(path_spec, u'mft_entry', None)

    if (location == self.LOCATION_ROOT or
        mft_entry == self.MFT_ENTRY_ROOT_DIRECTORY):
      fsntfs_file_entry = self._fsntfs_volume.get_root_directory()
      return dfvfs.vfs.ntfs_file_entry.NTFSFileEntry(
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
      return

    return dfvfs.vfs.ntfs_file_entry.NTFSFileEntry(
        self._resolver_context, self, path_spec,
        fsntfs_file_entry=fsntfs_file_entry)

  def GetNTFSVolume(self):
    """Retrieves the file system info object.

    Returns:
      The NTFS volume object (instance of pyfsntfs.volume).
    """
    return self._fsntfs_volume

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry).
    """
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=self.LOCATION_ROOT, mft_entry=self.MFT_ENTRY_ROOT_DIRECTORY,
        parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
