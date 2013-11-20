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
"""The operating system path specification implementation."""

from pyvfs.path import path_spec


class OSPathSpec(path_spec.PathSpec):
  """The operating system path specification implementation."""

  def __init__(self, location, parent=None):
    """Initializes the operating system path specification object.

    Args:
      location: the operating specific location string e.g. /usr/lib/pyvfs.
      parent: optional parent path specification (instance of PathSpec),
              default is None.
    """
    super(OSPathSpec, self).__init__(parent=parent)
    self.location = location
