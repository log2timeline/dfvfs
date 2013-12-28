#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The PyVFS Project Authors.
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
"""The VSS path specification resolver helper implementation."""

import pyvshadow

# This is necessary to prevent a circular import.
import pyvfs.file_io.vshadow_file_io
import pyvfs.vfs.vshadow_file_system

from pyvfs.lib import definitions
from pyvfs.lib import errors
from pyvfs.resolver import resolver
from pyvfs.resolver import resolver_helper


if pyvshadow.get_version() < '20131209':
  raise ImportWarning(
      'VShadowResolverHelper requires at least pyvshadow 20131209.')


class VShadowResolverHelper(resolver_helper.ResolverHelper):
  """Class that implements the Volume Shadow Snapshots (VSS) resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VSHADOW

  def OpenFileObject(self, path_spec):
    """Opens a file-like object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).

    Returns:
      The file-like object (instance of file_io.FileIO) or None if the path
      specification could not be resolved.
    """
    file_object = pyvfs.file_io.vshadow_file_io.VShadowFile()
    file_object.open(path_spec)
    return file_object

  def OpenFileSystem(self, path_spec):
    """Opens a file system object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).

    Returns:
      The file system object (instance of vfs.VShadowFileSystem) or None if
      the path specification could not be resolved.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification without parent.')

    file_object = resolver.Resolver.OpenFileObject(path_spec.parent)
    vshadow_volume = pyvshadow.volume()
    vshadow_volume.open_file_object(file_object)
    return pyvfs.vfs.vshadow_file_system.VShadowFileSystem(
        vshadow_volume, path_spec.parent)

# Register the resolver helpers with the resolver.
resolver.Resolver.RegisterHelper(VShadowResolverHelper())
