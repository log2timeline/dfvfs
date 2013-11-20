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
"""The Virtual File System (VFS) path specification object interface."""

# TODO: add serialization support.


class PathSpec(object):
  """The path specification object interface."""

  def __init__(self, parent=None):
    """Initializes the path specification object.

    Args:
      parent: optional parent path specification (instance of PathSpec),
              default is None.
    """
    super(PathSpec, self).__init__()
    self.parent = parent

  def HasParent(self):
    """Determines if the path specfication has a parent."""
    return self.parent is not None
