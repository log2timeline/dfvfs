#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 The dfVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The mount path specification resolver helper implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.mount import manager as mount_manager
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


class MountResolverHelper(resolver_helper.ResolverHelper):
  """Class that implements the mount resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_MOUNT

  def OpenFileObject(self, path_spec, resolver_context):
    """Opens a file-like object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file-like object (instance of file_io.FileIO) or None if the path
      specification could not be resolved.

    Raises:
      MountPointError: if the mount point is incorrect.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification or mode is invalid.
    """
    if not path_spec:
      raise ValueError(u'Missing path specfication.')

    if path_spec.HasParent():
      raise errors.PathSpecError(u'Unsupported path specification with parent.')

    mount_point = getattr(path_spec, 'identifier', None)
    if not mount_point:
      raise errors.PathSpecError(
          u'Unsupported path specification without mount point identifier.')

    mount_path_spec = mount_manager.MountPointManager.GetMountPoint(mount_point)
    if not mount_path_spec:
      raise errors.MountPointError(
          u'No such mount point: {0:s}'.format(mount_point))

    return resolver.Resolver.OpenFileObject(
        mount_path_spec, resolver_context=resolver_context)

  def OpenFileSystem(self, path_spec, resolver_context):
    """Opens a file system object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file system object (instance of vfs.FileSystem) or None if
      the path specification could not be resolved.

    Raises:
      MountPointError: if the mount point is incorrect.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification or mode is invalid.
    """
    if not path_spec:
      raise ValueError(u'Missing path specfication.')

    if path_spec.HasParent():
      raise errors.PathSpecError(u'Unsupported path specification with parent.')

    mount_point = getattr(path_spec, 'identifier', None)
    if not mount_point:
      raise errors.PathSpecError(
          u'Unsupported path specification without mount point identifier.')

    mount_path_spec = mount_manager.MountPointManager.GetMountPoint(mount_point)
    if not mount_path_spec:
      raise errors.MountPointError(
          u'No such mount point: {0:s}'.format(mount_point))

    return resolver.Resolver.OpenFileSystem(
        mount_path_spec, resolver_context=resolver_context)


# Register the resolver helpers with the resolver.
resolver.Resolver.RegisterHelper(MountResolverHelper())
