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
"""The Virtual File System (VFS) path specification factory object."""


class Factory(object):
  """Class that implements the VFS path specification factory."""

  PROPERTY_NAMES = frozenset([
      'compression_method', 'identifier', 'inode', 'location', 'part_index',
      'range_offset', 'range_size', 'start_offset', 'store_index'])

  _path_spec_types = {}

  @classmethod
  def DeregisterHelper(cls, path_spec_type):
    """Deregisters a path specification.

    Args:
      path_spec_type: the VFS path specification type (or class) object.

    Raises:
      KeyError: if path specification is not registered.
    """
    if path_spec_type.TYPE_INDICATOR not in cls._path_spec_types:
      raise KeyError((
          u'Path specification type: {0:s} not set.').format(
              path_spec_type.TYPE_INDICATOR))

    del cls._path_spec_types[path_spec_type.TYPE_INDICATOR]

  @classmethod
  def GetProperties(cls, path_spec):
    """Retrieves a dictionary containing the path specfication properties.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Raises:
      A dictionary object containing the properties.
    """
    properties = {}

    for property_name in cls.PROPERTY_NAMES:
      # Note that we don't want to set the properties when not used.
      if hasattr(path_spec, property_name):
        properties[property_name] = getattr(path_spec, property_name)

    return properties

  @classmethod
  def NewPathSpec(cls, type_indicator, **kwargs):
    """Creates a new path specification for the specific type indicator.

    Args:
      type_indicator: the VFS path specification type indicator.
      kwargs: a dictionary of keyword arguments dependending on the path
              specification.

    Returns:
      The VFS path specification (instance of path.PathSpec).

    Raises:
      KeyError: if path specification is not registered.
    """
    if type_indicator not in cls._path_spec_types:
      raise KeyError((
          u'Path specification type: {0:s} not set.').format(type_indicator))

    # An empty parent will cause parentless path specifications to raise
    # so we conveniently remove it here.
    if 'parent' in kwargs and kwargs['parent'] is None:
      del kwargs['parent']

    path_spec_type = cls._path_spec_types[type_indicator]
    return path_spec_type(**kwargs)

  @classmethod
  def RegisterPathSpec(cls, path_spec_type):
    """Registers a path specification type.

    Args:
      path_spec_type: the VFS path specification type (or class) object.

    Raises:
      KeyError: if path specification is already registered.
    """
    if path_spec_type.TYPE_INDICATOR in cls._path_spec_types:
      raise KeyError((
          u'Path specification type: {0:s} already set.').format(
              path_spec_type.TYPE_INDICATOR))

    cls._path_spec_types[path_spec_type.TYPE_INDICATOR] = path_spec_type
