# -*- coding: utf-8 -*-
"""The CPIO file system implementation."""

# This is necessary to prevent a circular import.
import dfvfs.vfs.cpio_file_entry

from dfvfs.lib import cpio
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import cpio_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system


class CPIOFileSystem(file_system.FileSystem):
  """Class that implements a file system object using CPIOArchiveFile."""

  LOCATION_ROOT = u'/'
  TYPE_INDICATOR = definitions.TYPE_INDICATOR_CPIO

  def __init__(self, resolver_context, encoding=u'utf-8'):
    """Initializes a file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      encoding: optional file entry name encoding.
    """
    super(CPIOFileSystem, self).__init__(resolver_context)
    self._cpio_archive_file = None
    self._file_object = None
    self.encoding = encoding

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._cpio_archive_file.Close()
    self._cpio_archive_file = None

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
      path_spec: a path specification (instance of PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    location = getattr(path_spec, u'location', None)

    if (location is None or
        not location.startswith(self.LOCATION_ROOT)):
      return

    if len(location) == 1:
      return True

    return self._cpio_archive_file.FileEntryExistsByPath(location[1:])

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      A file entry (instance of vfs.CPIOFileEntry) or None.
    """
    cpio_archive_file_entry = None
    location = getattr(path_spec, u'location', None)

    if (location is None or
        not location.startswith(self.LOCATION_ROOT)):
      return

    if len(location) == 1:
      return dfvfs.vfs.cpio_file_entry.CPIOFileEntry(
          self._resolver_context, self, path_spec, is_root=True,
          is_virtual=True)

    cpio_archive_file_entry = self._cpio_archive_file.GetFileEntryByPath(
        location[1:])
    if cpio_archive_file_entry is None:
      return
    return dfvfs.vfs.cpio_file_entry.CPIOFileEntry(
        self._resolver_context, self, path_spec,
        cpio_archive_file_entry=cpio_archive_file_entry)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry).
    """
    path_spec = cpio_path_spec.CPIOPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)

  def GetCPIOArchiveFile(self):
    """Retrieves the CPIO archive file object.

    Returns:
      The CPIO archvie file object (instance of cpio.CPIOArchiveFile).
    """
    return self._cpio_archive_file
