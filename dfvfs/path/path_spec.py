#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The dfVFS Project Authors.
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


class PathSpec(object):
  """Class that implements the path specification object interface."""

  def __init__(self, parent=None, **kwargs):
    """Initializes the path specification object.

    Args:
      parent: optional parent path specification (instance of PathSpec),
              default is None.
      kwargs: a dictionary of keyword arguments dependending on the path
              specification.

    Raises:
      ValueError: when there are unused keyword arguments.
    """
    if kwargs:
      raise ValueError(u'Unused keyword arguments.')

    super(PathSpec, self).__init__()
    self.parent = parent

  def __eq__(self, other):
    """Determines if the path specification is equal to the other."""
    return self.comparable == other.comparable

  def __hash__(self):
    """Returns the hash of a path specification."""
    return hash(self.comparable)

  def _GetComparable(self, sub_comparable_string=u''):
    """Retrieves the comparable representation.

       This is a convenince function for constructing comparables.

    Args:
      sub_comparable_string: the sub comparable string. The default is
                             an empty string.

    Returns:
      A string containing the comparable.
    """
    string_parts = []

    string_parts.append(getattr(self.parent, 'comparable', u''))
    string_parts.append(u'type: {0:s}'.format(self.type_indicator))

    if sub_comparable_string:
      string_parts.append(u', {0:s}'.format(sub_comparable_string))
    string_parts.append(u'\n')

    return u''.join(string_parts)

  @abc.abstractproperty
  def comparable(self):
    """Comparable representation of the path specification."""

  @property
  def type_indicator(self):
    """The type indicator."""
    type_indicator = getattr(self, 'TYPE_INDICATOR', None)
    if type_indicator is None:
      raise NotImplementedError(
          u'Invalid path specification missing type indicator.')
    return type_indicator

  def HasParent(self):
    """Determines if the path specfication has a parent."""
    return self.parent is not None
