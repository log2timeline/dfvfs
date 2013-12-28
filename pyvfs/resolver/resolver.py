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
"""The Virtual File System (VFS) path specification resolver object."""


class Resolver(object):
  """Class that implements the VFS path specification resolver."""

  _resolver_helpers = {}

  @classmethod
  def DeregisterHelper(cls, resolver_helper):
    """Deregisters a path specification resolver helper.

    Args:
      resolver_helper: the resolver helper object (instance of
                       resolver.ResolverHelper).

    Raises:
      KeyError: if resolver helper object is not set for the corresponding
                type indicator.
    """
    if resolver_helper.type_indicator not in cls._resolver_helpers:
      raise KeyError((
          u'Resolver helper object not set for type indicator: {0:s}.').format(
              resolver_helper.type_indicator))

    del cls._resolver_helpers[resolver_helper.type_indicator]

  @classmethod
  def OpenFileObject(cls, path_spec):
    """Opens a file-like object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).

    Returns:
      The file-like object (instance of file.FileIO) or None if the path
      specification could not be resolved.

    Raises:
      KeyError: if resolver helper object is not set for the corresponding
                type indicator.
    """
    if path_spec.type_indicator not in cls._resolver_helpers:
      raise KeyError((
          u'Resolver helper object not set for type indicator: {0:s}.').format(
              path_spec.type_indicator))

    resolver_helper = cls._resolver_helpers[path_spec.type_indicator]

    return resolver_helper.OpenFileObject(path_spec)

  @classmethod
  def OpenFileSystem(cls, path_spec):
    """Opens a file system object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).

    Returns:
      The file system object (instance of vfs.FileSystem) or None if the path
      specification could not be resolved or has no file system object.

    Raises:
      KeyError: if resolver helper object is not set for the corresponding
                type indicator.
    """
    if path_spec.type_indicator not in cls._resolver_helpers:
      raise KeyError((
          u'Resolver helper object not set for type indicator: {0:s}.').format(
              path_spec.type_indicator))

    resolver_helper = cls._resolver_helpers[path_spec.type_indicator]

    return resolver_helper.OpenFileSystem(path_spec)

  @classmethod
  def RegisterHelper(cls, resolver_helper):
    """Registers a path specification resolver helper.

    Args:
      resolver_helper: the resolver helper object (instance of
                       resolver.ResolverHelper).

    Raises:
      KeyError: if resolver helper object is already set for the corresponding
                type indicator.
    """
    if resolver_helper.type_indicator in cls._resolver_helpers:
      raise KeyError((
          u'Resolver helper object already set for type indicator: '
          u'{0:s}.').format(resolver_helper.type_indicator))

    cls._resolver_helpers[resolver_helper.type_indicator] = resolver_helper
