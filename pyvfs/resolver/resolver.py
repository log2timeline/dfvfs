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
  def RegisterHelper(cls, resolver_helper):
    """Registers a path spefication resolving helper function.

    Args:
      resolver_helper: the resolver helper object (instance of
                       vfs.ResolverHelper).

    Raises:
      KeyError: if resolver helper object is already set for the corresponding
                path specification class.
    """
    if resolver_helper.class_name in cls._resolver_helpers:
      raise KeyError((
          u'Resolver object already set for path specification class: '
          u'{0:s}').format(resolver_helper.class_name))

    cls._resolver_helpers[resolver_helper.class_name] = resolver_helper

  @classmethod
  def DeregisterHelper(cls, resolver_helper):
    """Deregisters a path spefication resolving helper function.

    Args:
      resolver_helper: the resolver helper object (instance of
                       vfs.ResolverHelper).

    Raises:
      KeyError: if resolver helper object is not set for the corresponding
                path specification class.
    """
    if resolver_helper.class_name not in cls._resolver_helpers:
      raise KeyError((
          u'Resolver object not set for path specification class: '
          u'{0:s}').format(resolver_helper.class_name))

    del cls._resolver_helpers[resolver_helper.class_name]

  @classmethod
  def OpenPathSpec(cls, path_spec):
    """Opens a file-like object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).

    Returns:
      The file-like object (instance of file.FileIO) or None if the path
      specification could not be resolved.

    Raises:
      KeyError: if resolver helper object is not set for the corresponding
                path specification class.
    """
    if path_spec.type_identifier not in cls._resolver_helpers:
      raise KeyError((
          u'Resolver object not set for path specification class: '
          u'{0:s}').format(path_spec.type_identifier))

    resolver_helper = cls._resolver_helpers[path_spec.type_identifier]

    return resolver_helper.OpenPathSpec(path_spec)
