# -*- coding: utf-8 -*-
"""The VHD image file-like object."""

import pyvhdi

from dfvfs import dependencies
from dfvfs.file_io import file_object_io
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver


dependencies.CheckModuleVersion(u'pyvhdi')


class VHDIFile(file_object_io.FileObjectIO):
  """Class that implements a file-like object using pyvhdi."""

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

    vhdi_file = pyvhdi.file()
    vhdi_file.open_file_object(file_object)

    if vhdi_file.parent_identifier:
      parent_location = getattr(path_spec, u'location', None)
      if not parent_location:
        raise errors.PathSpecError(
            u'Unsupported parent path specification without location.')

      file_system = resolver.Resolver.OpenFileSystem(
          path_spec, resolver_context=self._resolver_context)

      location_path_segments = file_system.SplitPath(parent_location)

      parent_filename = vhdi_file.parent_filename
      _, _, parent_filename = parent_filename.rpartition(u'\\')

      # The last parent location path segment contains the extent data filename.
      # Since we want to check if the next extent data file exists we remove
      # the previous one form the path segments list and add the new filename.
      # After that the path segments list can be used to create the location
      # string.
      location_path_segments.pop()
      location_path_segments.append(parent_filename)
      parent_file_location = file_system.JoinPath(location_path_segments)

      # Note that we don't want to set the keyword arguments when not used
      # because the path specification base class will check for unused
      # keyword arguments and raise.
      kwargs = path_spec_factory.Factory.GetProperties(path_spec)

      kwargs[u'location'] = parent_file_location
      if path_spec.parent is not None:
        kwargs[u'parent'] = path_spec.parent

      parent_file_path_spec = path_spec_factory.Factory.NewPathSpec(
          path_spec.type_indicator, **kwargs)

      if file_system.FileEntryExistsByPathSpec(parent_file_path_spec):
        file_object = resolver.Resolver.OpenFileObject(
            parent_file_path_spec, resolver_context=self._resolver_context)

        vhdi_parent_file = pyvhdi.file()
        vhdi_parent_file.open_file_object(file_object)

        vhdi_file.set_parent(vhdi_parent_file)

    return vhdi_file

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._file_object.get_media_size()
