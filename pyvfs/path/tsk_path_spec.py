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
"""The SleuthKit path specification implementation."""

from pyvfs.path import path_spec


PATH_SEPARATOR = u'/'


class TSKPathSpec(path_spec.PathSpec):
  """Class that implements the SleuthKit path specification."""

  def __init__(self, inode=None, location=None, parent=None):
    """Initializes the path specification object.

       The SleuthKit path specification object allows to specify a path
       interpreted by SleuthKit specific VFS classes. The path can be
       specified as either a location string or an inode number. Note
       that looking up an inode number in SleuthKit can be faster than
       looking up a location string.

    Args:
      inode: optional SleuthKit inode string.
      location: optional SleuthKit location string.
      parent: optional parent path specification (instance of PathSpec),
              default is None.

    Raises:
      ValueError: when inode and location are both not set.
    """
    if not inode and not location:
      raise ValueError(u'Missing inode and location value.')

    super(TSKPathSpec, self).__init__(parent=parent)
    self.inode = inode
    self.location = location

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    return self._GetComparable(
        u'inode: {0:d}, location: {1:s}\n'.format(self.inode, self.location))
