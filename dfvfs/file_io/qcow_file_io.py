# -*- coding: utf-8 -*-
"""The QCOW image file-like object."""

import pyqcow

from dfvfs import dependencies
from dfvfs.file_io import file_object_io
from dfvfs.lib import errors
from dfvfs.resolver import resolver


dependencies.CheckModuleVersion(u'pyqcow')


class QCOWFile(file_object_io.FileObjectIO):
  """Class that implements a file-like object using pyqcow."""

  def _OpenFileObject(self, path_spec):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).

    Returns:
      A file-like object.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification without parent.')

    file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)
    qcow_file = pyqcow.file()
    qcow_file.open_file_object(file_object)
    return qcow_file

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._file_object.get_media_size()
