# -*- coding: utf-8 -*-
"""The gzip file entry implementation."""

from __future__ import unicode_literals

from dfdatetime import posix_time as dfdatetime_posix_time

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.resolver import resolver
from dfvfs.vfs import root_only_file_entry


class GzipFileEntry(root_only_file_entry.RootOnlyFileEntry):
  """File system file entry that uses gzip."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_GZIP

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file

    Raises:
      BackEndError: when the gzip file is missing.
    """
    gzip_file = resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=resolver_context)
    if not gzip_file:
      raise errors.BackEndError('Missing gzip file.')

    super(GzipFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._gzip_file = gzip_file
    self._type = definitions.FILE_ENTRY_TYPE_FILE

  def __del__(self):
    """Cleans up the file entry."""
    # __del__ can be invoked before __init__ has completed.
    if hasattr(self, '_gzip_file'):
      self._gzip_file.close()
      self._gzip_file = None

    super(GzipFileEntry, self).__del__()

  def _GetStat(self):
    """Retrieves information about the file entry.

    Returns:
      VFSStat: a stat object.
    """
    stat_object = super(GzipFileEntry, self)._GetStat()

    if self._gzip_file:
      stat_object.size = self._gzip_file.uncompressed_data_size

    # Other stat information.
    # gzip_file.comment
    # gzip_file.operating_system
    # gzip_file.original_filename

    return stat_object

  @property
  def modification_time(self):
    """dfdatetime.DateTimeValues: modification time or None if not available."""
    timestamp = getattr(self._gzip_file, 'modification_time', None)
    if timestamp is not None:
      return dfdatetime_posix_time.PosixTime(timestamp=timestamp)
