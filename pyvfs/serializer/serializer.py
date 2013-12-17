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
"""The Virtual File System (VFS) serializer object interfaces."""

import abc


class PathSpecSerializer(object):
  """Class that implements the path specification serializer interface."""

  @abc.abstractmethod
  def ReadSerialized(self, serialized):
    """Reads a path specification from serialized form.

    Args:
      serialized: an object containing the serialized form.

    Returns:
      A path specification (instance of path.PathSpec).
    """

  @abc.abstractmethod
  def WriteSerialized(self, path_spec):
    """Writes a path specification to serialized form.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      An object containing the serialized form.
    """
