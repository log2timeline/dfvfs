# -*- coding: utf-8 -*-
"""The Mac OS disk image file-like object."""

import pymodi

from dfvfs.file_io import file_object_io
from dfvfs.lib import errors
from dfvfs.resolver import resolver


class MODIFile(file_object_io.FileObjectIO):
  """File input/output (IO) object using pymodi."""

  def __init__(self, resolver_context, path_spec):
    """Initializes a file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(MODIFile, self).__init__(resolver_context, path_spec)
    self._sub_file_objects = []

  def _Close(self):
    """Closes the file-like object."""
    super(MODIFile, self)._Close()
    self._sub_file_objects = []

  def _OpenFileObject(self, path_spec):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      pymodi.handle: a file-like object.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)

    modi_file = pymodi.handle()
    modi_file.open_file_object(file_object)

    self._sub_file_objects.append(file_object)
    self._sub_file_objects.reverse()

    return modi_file

  def get_size(self):
    """Retrieves the size of the file-like object.

    Returns:
      int: size of the file-like object data.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    return self._file_object.get_media_size()
