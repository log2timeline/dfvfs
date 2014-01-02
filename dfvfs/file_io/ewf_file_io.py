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
"""The EWF image file-like object."""

import pyewf

from dfvfs.file_io import file_object_io
from dfvfs.lib import errors
from dfvfs.resolver import resolver


if pyewf.get_version() < '20131210':
  raise ImportWarning('EwfFile requires at least pyewf 20131210.')


class EwfFile(file_object_io.FileObjectIO):
  """Class that implements a file-like object using pyewf."""

  def _OpenFileObject(self, path_spec):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: the path specification (instance of path.PathSpec).

    Returns:
      A file-like object.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification without parent.')

    # TODO: handle multiple segment file here.
    # Glob first then resolve the file objects of every segment file?
    file_object = resolver.Resolver.OpenFileObject(path_spec.parent)
    ewf = pyewf.handle()
    ewf.open_file_objects([file_object])
    return ewf

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._file_object.get_media_size()
