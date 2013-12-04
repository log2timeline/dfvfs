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
"""The tar path specification implementation."""

from pyvfs.path import location_path_spec


PATH_SEPARATOR = u'/'


class TarPathSpec(location_path_spec.LocationPathSpec):
  """Class that implements the tar file path specification."""

  def __init__(self, location, parent):
    """Initializes the path specification object.

       Note that the tar file path specification must have a parent.

    Args:
      location: the tar file internal location string prefixed with a path
                separator character.
      parent: parent path specification (instance of PathSpec).

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError(u'Missing parent value.')

    super(TarPathSpec, self).__init__(location, parent=parent)
