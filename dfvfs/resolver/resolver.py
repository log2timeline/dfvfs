#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The dfVFS Project Authors.
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

from dfvfs.resolver import context


class Resolver(object):
  """Class that implements the VFS path specification resolver."""

  _resolver_context = context.Context()
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
  def OpenFileEntry(cls, path_spec, resolver_context=None):
    """Opens a file entry object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).
      resolver_context: the optional resolver context (instance of
                        resolver.Context). The default is None which will use
                        the built in context which is not multi process safe.

    Returns:
      The file entry object (instance of vfs.FileEntry) or None if the path
      specification could not be resolved.
    """
    file_system = cls.OpenFileSystem(
        path_spec, resolver_context=resolver_context)
    if file_system is None:
      return

    if resolver_context is None:
      resolver_context = cls._resolver_context

    # TODO: add file entry context support?
    return file_system.GetFileEntryByPathSpec(path_spec)

  @classmethod
  def OpenFileObject(cls, path_spec, resolver_context=None):
    """Opens a file-like object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).
      resolver_context: the optional resolver context (instance of
                        resolver.Context). The default is None which will use
                        the built in context which is not multi process safe.

    Returns:
      The file-like object (instance of file.FileIO) or None if the path
      specification could not be resolved.

    Raises:
      KeyError: if resolver helper object is not set for the corresponding
                type indicator.
    """
    if resolver_context is None:
      resolver_context = cls._resolver_context

    file_object = resolver_context.GetFileObject(path_spec)

    if file_object is None:
      if path_spec.type_indicator not in cls._resolver_helpers:
        raise KeyError((
            u'Resolver helper object not set for type indicator: '
            u'{0:s}.').format(path_spec.type_indicator))

      resolver_helper = cls._resolver_helpers[path_spec.type_indicator]
      file_object = resolver_helper.OpenFileObject(path_spec, resolver_context)
      resolver_context.CacheFileObject(path_spec, file_object)

    return file_object

  @classmethod
  def OpenFileSystem(cls, path_spec, resolver_context=None):
    """Opens a file system object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).
      resolver_context: the optional resolver context (instance of
                        resolver.Context). The default is None which will use
                        the built in context which is not multi process safe.

    Returns:
      The file system object (instance of vfs.FileSystem) or None if the path
      specification could not be resolved or has no file system object.

    Raises:
      KeyError: if resolver helper object is not set for the corresponding
                type indicator.
    """
    if resolver_context is None:
      resolver_context = cls._resolver_context

    file_system = resolver_context.GetFileSystem(path_spec)

    if file_system is None:
      if path_spec.type_indicator not in cls._resolver_helpers:
        raise KeyError((
            u'Resolver helper object not set for type indicator: '
            u'{0:s}.').format(path_spec.type_indicator))

      resolver_helper = cls._resolver_helpers[path_spec.type_indicator]
      file_system = resolver_helper.OpenFileSystem(path_spec, resolver_context)
      resolver_context.CacheFileSystem(path_spec, file_system)

    return file_system

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
