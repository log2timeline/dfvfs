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
"""The zip path specification implementation."""

from pyvfs.lib import definitions
from pyvfs.path import factory
from pyvfs.path import location_path_spec


class ZipPathSpec(location_path_spec.LocationPathSpec):
  """Class that implements the zip file path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ZIP

  def __init__(self, location=None, parent=None, **kwargs):
    """Initializes the path specification object.

       Note that the zip file path specification must have a parent.

    Args:
      location: optional zip file internal location string prefixed with a path
                separator character. The default is None.
      parent: optional parent path specification (instance of PathSpec).
              The default None.
      kwargs: a dictionary of keyword arguments dependending on the path
              specification

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError(u'Missing parent value.')

    super(ZipPathSpec, self).__init__(
        location=location, parent=parent, **kwargs)


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(ZipPathSpec)
