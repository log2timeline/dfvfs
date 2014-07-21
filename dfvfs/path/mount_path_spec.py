#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 The dfVFS Project Authors.
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
"""The mount path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class MountPathSpec(path_spec.PathSpec):
  """Class that implements the mount path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_MOUNT

  def __init__(self, identifier, **kwargs):
    """Initializes the path specification object.

       Note that the mount path specification cannot have a parent.

    Args:
      identifier: the identifier of the mount point.
      kwargs: a dictionary of keyword arguments dependending on the path
              specification.

    Raises:
      ValueError: when identifier is not set.
    """
    if not identifier:
      raise ValueError(u'Missing identifier value.')

    super(MountPathSpec, self).__init__(parent=None, **kwargs)
    self.identifier = identifier

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    sub_comparable_string = u'identifier: {0:s}'.format(self.identifier)
    return self._GetComparable(sub_comparable_string=sub_comparable_string)


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(MountPathSpec)
