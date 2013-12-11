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

from pyvfs.path import path_spec


class VShadowPathSpec(path_spec.PathSpec):
  """Class that implements the VSS path specification."""

  def __init__(self, store_index, parent):
    """Initializes the path specification object.

    Args:
      store_index: the store index.
      parent: the parent path specification (instance of PathSpec).
    """
    super(VShadowPathSpec, self).__init__(parent=parent)
    self.store_index = store_index

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    sub_comparable_string = u'store: {0:d}'.format(self.store_index)
    return self._GetComparable(sub_comparable_string)
