# -*- coding: utf-8 -*-
"""The RAW storage media image file-like object implementation."""

import pysmraw

from dfvfs.file_io import file_object_io
from dfvfs.lib import errors
from dfvfs.lib import raw
from dfvfs.resolver import resolver


if pysmraw.get_version() < '20140614':
  raise ImportWarning('RawFile requires at least pysmraw 20140614.')


class RawFile(file_object_io.FileObjectIO):
  """Class that implements a file-like object using pysmraw."""

  def _OpenFileObject(self, path_spec):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: the path specification (instance of path.PathSpec).

    Returns:
      A file-like object or None.

    Raises:
      PathSpecError: if the path specification is invalid.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification without parent.')

    parent_path_spec = path_spec.parent

    file_system = resolver.Resolver.OpenFileSystem(
        parent_path_spec, resolver_context=self._resolver_context)

    # Note that we cannot use pysmraw's glob function since it does not
    # handle the file system abstraction dfvfs provides.
    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    if not segment_file_path_specs:
      return

    file_objects = []
    for segment_file_path_spec in segment_file_path_specs:
      file_object = resolver.Resolver.OpenFileObject(
          segment_file_path_spec, resolver_context=self._resolver_context)
      file_objects.append(file_object)

    raw_handle = pysmraw.handle()
    raw_handle.open_file_objects(file_objects)
    return raw_handle

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._file_object.get_media_size()
