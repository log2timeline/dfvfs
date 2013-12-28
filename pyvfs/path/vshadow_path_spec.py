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
"""The Volume Shadow Snapshots (VSS) path specification implementation."""

from pyvfs.lib import definitions
from pyvfs.path import factory
from pyvfs.path import path_spec


class VShadowPathSpec(path_spec.PathSpec):
  """Class that implements the VSS path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VSHADOW

  def __init__(self, location=None, store_index=None, parent=None, **kwargs):
    """Initializes the path specification object.

       Note that the VSS path specification must have a parent.

    Args:
      location: optional location string. The default is None.
      store_index: optional store index. The default is None.
      parent: optional parent path specification (instance of PathSpec).
              The default is None.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError(u'Missing parent value.')

    super(VShadowPathSpec, self).__init__(parent=parent, **kwargs)
    self.location = location
    self.store_index = store_index

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    string_parts = []

    if self.location is not None:
      string_parts.append(u'location: {0:s}'.format(self.location))
    if self.store_index is not None:
      string_parts.append(u'store: {0:d}'.format(self.store_index))

    return self._GetComparable(u', '.join(string_parts))


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(VShadowPathSpec)
