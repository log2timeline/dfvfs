# -*- coding: utf-8 -*-
"""The data range file system implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import data_range_path_spec
from dfvfs.vfs import data_range_file_entry
from dfvfs.vfs import root_only_file_system


class DataRangeFileSystem(root_only_file_system.RootOnlyFileSystem):
  """Class that implements a compresses stream file system object."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_DATA_RANGE

  def __init__(self, resolver_context):
    """Initializes a file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(DataRangeFileSystem, self).__init__(resolver_context)
    self._range_offset = None
    self._range_size = None

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._range_offset = None
    self._range_size = None

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
          'Unsupported path specification without parent.')

    range_offset = getattr(path_spec, 'range_offset', None)
    if range_offset is None:
      raise errors.PathSpecError(
          'Unsupported path specification without encoding method.')

    range_size = getattr(path_spec, 'range_size', None)
    if range_size is None:
      raise errors.PathSpecError(
          'Unsupported path specification without encoding method.')

    self._range_offset = range_offset
    self._range_size = range_size

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    return data_range_file_entry.DataRangeFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    path_spec = data_range_path_spec.DataRangePathSpec(
        range_offset=self._range_offset,
        range_size=self._range_size,
        parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
