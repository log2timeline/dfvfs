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

from pyvfs.lib import definitions
from pyvfs.path import factory
from pyvfs.path import path_spec


class CompressedStreamPathSpec(path_spec.PathSpec):
  """Class that implements the compressed stream path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_COMPRESSED_STREAM

  def __init__(self, compression_method=None, parent=None, **kwargs):
    """Initializes the path specification object.

       Note that the compressed stream path specification must have a parent.

    Args:
      compression_method: optional method used to the compress the data.
                          The default is None.
      parent: optional parent path specification (instance of PathSpec).
              The default is None.
      kwargs: a dictionary of keyword arguments dependending on the path
              specification.

    Raises:
      ValueError: when compression method or parent are not set.
    """
    if not compression_method or not parent:
      raise ValueError(u'Missing compression method or parent value.')

    super(CompressedStreamPathSpec, self).__init__(parent=parent, **kwargs)
    self.compression_method = compression_method

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    return self._GetComparable(
        u'compression_method: {0:s}\n'.format(self.compression_method))


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(CompressedStreamPathSpec)
