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
"""The compressed stream path specification implementation."""

from pyvfs.path import path_spec


class CompressedStreamPathSpec(path_spec.PathSpec):
  """Class that implements the compressed stream path specification."""

  def __init__(self, compression_method, parent):
    """Initializes the compressed stream path specification object.

       Note that the compressed stream path specification must have a parent.

    Args:
      compression_method: the method used to the compress the data.
      parent: parent path specification (instance of PathSpec).

    Raises:
      ValueError: when compression method or parent are not set.
    """
    if not compression_method or not parent:
      raise ValueError(u'Missing compression method or parent value.')

    super(CompressedStreamPathSpec, self).__init__(parent=parent)
    self.compression_method = compression_method

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    return self._GetComparable(
        u'compression_method: {0:s}\n'.format(self.compression_method))
