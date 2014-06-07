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
"""The BitLocker Drive Encryption (BDE) file-like object."""

import pybde

from dfvfs.file_io import file_object_io
from dfvfs.lib import bde
from dfvfs.lib import errors
from dfvfs.resolver import resolver


if pybde.get_version() < '20140531':
  raise ImportWarning('BdeFile requires at least pybde 20140531.')


class BdeFile(file_object_io.FileObjectIO):
  """Class that implements a file-like object using pybde."""

  def _OpenFileObject(self, path_spec):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: the path specification (instance of path.PathSpec).

    Returns:
      A file-like object.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification without parent.')

    file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)
    bde_volume = pybde.volume()
    bde.BdeVolumeOpen(
        bde_volume, path_spec, file_object, resolver.Resolver.key_chain)
    return bde_volume
