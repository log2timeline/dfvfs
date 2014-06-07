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
"""The BitLocker Drive Encryption (BDE) path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class BdePathSpec(path_spec.PathSpec):
  """Class that implements the BDE path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BDE

  def __init__(
      self, password=None, recovery_password=None, startup_key=None,
      parent=None, **kwargs):
    """Initializes the path specification object.

       Note that the BDE path specification must have a parent.

    Args:
      password: optional password string. The default is None.
      recovery_password: optional recovery password string. The default is None.
      startup_key: optional startup key file path. The default is None.
      parent: optional parent path specification (instance of PathSpec).
              The default is None.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError(u'Missing parent value.')

    super(BdePathSpec, self).__init__(parent=parent, **kwargs)
    self.password = password
    self.recovery_password = recovery_password
    self.startup_key = startup_key

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    return self._GetComparable()


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(BdePathSpec)
