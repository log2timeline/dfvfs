# -*- coding: utf-8 -*-
"""The Virtual Hard Disk image file-like object."""

import pyvhdi

from dfvfs.file_io import file_object_io
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver


class VHDIFile(file_object_io.FileObjectIO):
  """File input/output (IO) object using pyvhdi."""

  def __init__(self, resolver_context, path_spec):
    """Initializes a file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(VHDIFile, self).__init__(resolver_context, path_spec)
    self._parent_vhdi_files = []
    self._sub_file_objects = []

  def _Close(self):
    """Closes the file-like object."""
    super(VHDIFile, self)._Close()

    for vhdi_file in self._parent_vhdi_files:
      vhdi_file.close()

    self._parent_vhdi_files = []
    self._sub_file_objects = []

  def _OpenFileObject(self, path_spec):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      pyvhdi.file: a file-like object.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)

    vhdi_file = pyvhdi.file()
    vhdi_file.open_file_object(file_object)

    if vhdi_file.parent_identifier:  # pylint: disable=using-constant-test
      file_system = resolver.Resolver.OpenFileSystem(
          path_spec.parent, resolver_context=self._resolver_context)

      self._OpenParentFile(file_system, path_spec.parent, vhdi_file)

    self._sub_file_objects.append(file_object)

    self._parent_vhdi_files.reverse()
    self._sub_file_objects.reverse()

    return vhdi_file

  def _OpenParentFile(self, file_system, path_spec, vhdi_file):
    """Opens the parent file.

    Args:
      file_system (FileSystem): file system of the VHDI file.
      path_spec (PathSpec): path specification of the VHDI file.
      vhdi_file (pyvhdi.file): VHDI file.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    location = getattr(path_spec, 'location', None)
    if not location:
      raise errors.PathSpecError(
          'Unsupported path specification without location.')

    location_path_segments = file_system.SplitPath(location)

    parent_filename = vhdi_file.parent_filename
    _, _, parent_filename = parent_filename.rpartition('\\')

    location_path_segments.pop()
    location_path_segments.append(parent_filename)
    parent_file_location = file_system.JoinPath(location_path_segments)

    # Note that we don't want to set the keyword arguments when not used
    # because the path specification base class will check for unused
    # keyword arguments and raise.
    kwargs = path_spec_factory.Factory.GetProperties(path_spec)

    kwargs['location'] = parent_file_location
    if path_spec.parent is not None:
      kwargs['parent'] = path_spec.parent

    parent_file_path_spec = path_spec_factory.Factory.NewPathSpec(
        path_spec.type_indicator, **kwargs)

    if not file_system.FileEntryExistsByPathSpec(parent_file_path_spec):
      return

    file_object = resolver.Resolver.OpenFileObject(
        parent_file_path_spec, resolver_context=self._resolver_context)

    vhdi_parent_file = pyvhdi.file()
    vhdi_parent_file.open_file_object(file_object)

    if vhdi_parent_file.parent_identifier:  # pylint: disable=using-constant-test
      self._OpenParentFile(
          file_system, parent_file_path_spec, vhdi_parent_file)

    vhdi_file.set_parent(vhdi_parent_file)

    self._parent_vhdi_files.append(vhdi_parent_file)
    self._sub_file_objects.append(file_object)

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
