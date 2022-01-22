# -*- coding: utf-8 -*-
"""The RAW storage media image file-like object implementation."""

import pysmraw

from dfvfs.file_io import file_object_io
from dfvfs.lib import errors
from dfvfs.lib import raw_helper
from dfvfs.resolver import resolver


class RawFile(file_object_io.FileObjectIO):
  """File input/output (IO) object using pysmraw."""

  def __init__(self, resolver_context, path_spec):
    """Initializes a file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(RawFile, self).__init__(resolver_context, path_spec)
    self._file_objects = []

  def _Close(self):
    """Closes the file-like object."""
    # pylint: disable=protected-access
    super(RawFile, self)._Close()
    self._file_objects = []

  def _OpenFileObject(self, path_spec):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      pysmraw.handle: a file-like object or None.

    Raises:
      PathSpecError: if the path specification is invalid.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    parent_path_spec = path_spec.parent
    parent_location = getattr(parent_path_spec, 'location', None)

    if parent_location and parent_path_spec.IsSystemLevel():
      segment_file_paths = pysmraw.glob(parent_location)

      raw_handle = pysmraw.handle()
      raw_handle.open(segment_file_paths)

    else:
      # Note that we cannot use pysmraw's glob function here since it does
      # not handle the file system abstraction dfvfs provides.

      file_system = resolver.Resolver.OpenFileSystem(
          parent_path_spec, resolver_context=self._resolver_context)

      segment_file_path_specs = raw_helper.RawGlobPathSpec(
          file_system, path_spec)
      if not segment_file_path_specs:
        return None

      for segment_file_path_spec in segment_file_path_specs:
        file_object = resolver.Resolver.OpenFileObject(
            segment_file_path_spec, resolver_context=self._resolver_context)
        self._file_objects.append(file_object)

      raw_handle = pysmraw.handle()
      raw_handle.open_file_objects(self._file_objects)

    return raw_handle

  def get_size(self):
    """Retrieves the size of the file-like object.

    Returns:
      int: size of the RAW storage media image.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    return self._file_object.get_media_size()
