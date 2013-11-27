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

import abc

# TODO: add serialization support.


class PathSpec(object):
  """Class that implements the path specification object interface."""

  def __init__(self, parent=None):
    """Initializes the path specification object.

    Args:
      parent: optional parent path specification (instance of PathSpec),
              default is None.
    """
    super(PathSpec, self).__init__()
    self.parent = parent

  def _GetComparable(self, sub_comparable):
    """Retrieves the comparable representation.

       This is a convenince function for constructing comparables.

    Args:
      sub_comparable: 

    Returns:
      A string containing the comparable.

    Raises:
      ValueError: when sub comparable is not set.
    """ 
    if not sub_comparable:
      raise ValueError(u'Missing sub comparable value.')

    if self.parent:
      parent_comparable = self.parent.comparable
    else:
      parent_comparable = u''

    return u'type: {0:s}, {1:s}\n'.format(parent_comparable, sub_comparable)

  @abc.abstractproperty
  def comparable(self):
    """Comparable representation of the path specification.""" 
    if self.parent:
      parent_comparable = self.parent.comparable
    else:
      parent_comparable = u''

    return u'type: {0:s}, inode: {1:d}, location: {2:s}\n'.format(
        parent_comparable, self.type_identifier, self.inode, self.location)

  @property
  def type_identifier(self):
    """The type identifier."""
    return self.__class__.__name__

  def __eq__(self, other):
    """Determines if the path specification is equal to the other."""
    return self.comparable == other.comparable

  def __hash__(self):
    """Returns the hash of a path specification."""
    return hash(self.comparable)

  def HasParent(self):
    """Determines if the path specfication has a parent."""
    return self.parent is not None
