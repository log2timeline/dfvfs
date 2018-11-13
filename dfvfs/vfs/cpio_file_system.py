# -*- coding: utf-8 -*-
"""The CPIO archive file system implementation."""

from __future__ import unicode_literals

from dfvfs.lib import cpio
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import cpio_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import cpio_file_entry
from dfvfs.vfs import file_system


class CPIOFileSystem(file_system.FileSystem):
  """CPIO archive file system."""

  LOCATION_ROOT = '/'
  TYPE_INDICATOR = definitions.TYPE_INDICATOR_CPIO

  def __init__(self, resolver_context, encoding='utf-8'):
    """Initializes a CPIO archive file system.

    Args:
      resolver_context (Context): resolver context.
      encoding (Optional[str]): file entry name encoding.
    """
    super(CPIOFileSystem, self).__init__(resolver_context)
    self._cpio_archive_file = None
    self._file_object = None
    self.encoding = encoding

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    self._cpio_archive_file.Close()
    self._cpio_archive_file = None

    self._file_object.close()
    self._file_object = None

  def _Open(self, path_spec, mode='rb'):
    """Opens the file system defined by path specification.

    Args:
      path_spec (PathSpec): path specification.
      mode (Optional[str]): file access mode. The default is 'rb' which
          represents read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)

    cpio_archive_file = cpio.CPIOArchiveFile()
    try:
      cpio_archive_file.Open(file_object)
    except:
      file_object.close()
      raise

    self._file_object = file_object
    self._cpio_archive_file = cpio_archive_file

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      bool: True if the file entry exists.
    """
    location = getattr(path_spec, 'location', None)
    if location is None or not location.startswith(self.LOCATION_ROOT):
      return False

    if len(location) == 1:
      return True

    return self._cpio_archive_file.FileEntryExistsByPath(location[1:])

  def GetCPIOArchiveFile(self):
    """Retrieves the CPIO archive file.

    Returns:
      CPIOArchiveFile: a CPIO archvie file.
    """
    return self._cpio_archive_file

  def GetCPIOArchiveFileEntryByPathSpec(self, path_spec):
    """Retrieves the CPIO archive file entry for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      CPIOArchiveFileEntry: CPIO archive file entry or None if not available.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    location = getattr(path_spec, 'location', None)
    if location is None:
      raise errors.PathSpecError('Path specification missing location.')

    if not location.startswith(self.LOCATION_ROOT):
      raise errors.PathSpecError('Invalid location in path specification.')

    if len(location) == 1:
      return None

    return self._cpio_archive_file.GetFileEntryByPath(location[1:])

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      CPIOFileEntry: a file entry or None if not available.
    """
    location = getattr(path_spec, 'location', None)

    if (location is None or
        not location.startswith(self.LOCATION_ROOT)):
      return None

    if len(location) == 1:
      return cpio_file_entry.CPIOFileEntry(
          self._resolver_context, self, path_spec, is_root=True,
          is_virtual=True)

    cpio_archive_file_entry = self._cpio_archive_file.GetFileEntryByPath(
        location[1:])
    if cpio_archive_file_entry is None:
      return None

    return cpio_file_entry.CPIOFileEntry(
        self._resolver_context, self, path_spec,
        cpio_archive_file_entry=cpio_archive_file_entry)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      CPIOFileEntry: a file entry or None if not available.
    """
    path_spec = cpio_path_spec.CPIOPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
