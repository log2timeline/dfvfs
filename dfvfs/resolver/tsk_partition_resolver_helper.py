# -*- coding: utf-8 -*-
"""The TSK partition path specification resolver helper implementation."""

import pytsk3

# This is necessary to prevent a circular import.
import dfvfs.file_io.tsk_partition_file_io
import dfvfs.vfs.tsk_partition_file_system

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import tsk_image
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


class TSKPartitionResolverHelper(resolver_helper.ResolverHelper):
  """Class that implements the SleuthKit resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK_PARTITION

  def OpenFileObject(self, path_spec, resolver_context):
    """Opens a file-like object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file-like object (instance of file_io.FileIO) or None if the path
      specification could not be resolved.
    """
    file_object = dfvfs.file_io.tsk_partition_file_io.TSKPartitionFile(
        resolver_context)
    file_object.open(path_spec=path_spec)
    return file_object

  def OpenFileSystem(self, path_spec, resolver_context):
    """Opens a file system object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file system object (instance of vfs.TSKFileSystem) or None if
      the path specification could not be resolved.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification without parent.')

    file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=resolver_context)
    tsk_image_object = tsk_image.TSKFileSystemImage(file_object)
    tsk_volume = pytsk3.Volume_Info(tsk_image_object)
    return dfvfs.vfs.tsk_partition_file_system.TSKPartitionFileSystem(
        resolver_context, tsk_volume, path_spec.parent)

# Register the resolver helpers with the resolver.
resolver.Resolver.RegisterHelper(TSKPartitionResolverHelper())
