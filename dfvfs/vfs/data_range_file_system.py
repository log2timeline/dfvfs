# -*- coding: utf-8 -*-
"""The data range file system implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import data_range_path_spec
from dfvfs.vfs import data_range_file_entry
from dfvfs.vfs import root_only_file_system


class DataRangeFileSystem(root_only_file_system.RootOnlyFileSystem):
  """Data range file system."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_DATA_RANGE

  def __init__(self, resolver_context, path_spec):
    """Initializes a data range file system.

    Args:
      resolver_context (Context): a resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(DataRangeFileSystem, self).__init__(resolver_context, path_spec)
    self._range_offset = None
    self._range_size = None

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    self._range_offset = None
    self._range_size = None

  def _Open(self, mode='rb'):
    """Opens the file system defined by path specification.

    Args:
      mode (Optional[str]): file access mode. The default is 'rb' which
          represents read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not self._path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    range_offset = getattr(self._path_spec, 'range_offset', None)
    if range_offset is None:
      raise errors.PathSpecError(
          'Unsupported path specification without encoding method.')

    range_size = getattr(self._path_spec, 'range_size', None)
    if range_size is None:
      raise errors.PathSpecError(
          'Unsupported path specification without encoding method.')

    self._range_offset = range_offset
    self._range_size = range_size

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      DataRangeFileEntry: a file entry or None if not available.
    """
    return data_range_file_entry.DataRangeFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      DataRangeFileEntry: a file entry or None if not available.
    """
    path_spec = data_range_path_spec.DataRangePathSpec(
        range_offset=self._range_offset,
        range_size=self._range_size,
        parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
