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
"""The location-based path specification implementation."""

from pyvfs.path import path_spec


class LocationPathSpec(path_spec.PathSpec):
  """Base class for location-based path specifications."""

  def __init__(self, location=None, parent=None, **kwargs):
    """Initializes the path specification object.

    Args:
      location: optional location string. The default is None.
      parent: optional parent path specification (instance of PathSpec),
              default is None.
      kwargs: a dictionary of keyword arguments dependending on the path
              specification.

    Raises:
      ValueError: when location is not set.
    """
    if not location:
      raise ValueError(u'Missing location value.')

    super(LocationPathSpec, self).__init__(parent=parent, **kwargs)
    self.location = location

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    return self._GetComparable(u'location: {0:s}\n'.format(self.location))
