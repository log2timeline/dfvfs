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
"""The EWF image path specification implementation."""

from pyvfs.path import path_spec


class EwfPathSpec(path_spec.PathSpec):
  """Class that implements the EWF image path specification."""

  def __init__(self, parent):
    """Initializes the path specification object.

       Note that the ewf file path specification must have a parent.

    Args:
      parent: parent path specification (instance of PathSpec).

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError(u'Missing parent value.')

    super(EwfPathSpec, self).__init__(parent=parent)

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    return self._GetComparable(u'')
