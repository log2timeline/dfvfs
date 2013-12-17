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
"""The Virtual File System (VFS) resolver helper object interface."""

import abc


class ResolverHelper(object):
  """Class that implements the resolver helper object interface."""

  def __init__(self, type_indicator):
    """Initializes the resolver helper object.

    Args:
      type_indicator: the path specification type indicator.
    """
    super(ResolverHelper, self).__init__()
    self.type_indicator = type_indicator

  @abc.abstractmethod
  def OpenFileObject(self, path_spec):
    """Opens a file-like object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).

    Returns:
      The file-like object (instance of io.FileIO) or None if the path
      specification could not be resolved.
    """

  def OpenFileSystem(self, dummy_path_spec):
    """Opens a file system object defined by path specification.

       This is the fall through implementation function that raises
       a RuntimeError.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).

    Raises:
      RuntimeError: since this is the fall through implementation.
    """
    # Note: not using NotImplementedError here since pylint then will complain
    # derived classes will need to implement the function, which should not
    # be the the case.
    raise RuntimeError('Missing implemention to open file system.')
