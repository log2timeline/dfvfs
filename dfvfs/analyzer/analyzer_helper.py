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
"""The Virtual File System (VFS) analyzer helper object interface."""


class AnalyzerHelper(object):
  """Class that implements the analyzer helper object interface."""

  @property
  def format_categories(self):
    """The format categories."""
    format_categories = getattr(self, 'FORMAT_CATEGORIES', None)
    if format_categories is None:
      raise NotImplementedError(
          u'Invalid analyzer helper missing format categories.')
    return format_categories

  @property
  def type_indicator(self):
    """The type indicator."""
    type_indicator = getattr(self, 'TYPE_INDICATOR', None)
    if type_indicator is None:
      raise NotImplementedError(
          u'Invalid analyzer helper missing type indicator.')
    return type_indicator

  def AnalyzeFileObject(self, unused_file_object):
    """Retrieves the format specification.

       This is the fall through implementation that raises a RuntimeError.

    Args:
      unused_file_object: a file-like object (instance of file_io.FileIO).

    Returns:
      The type indicator if the file-like object contains a supported format
      or None otherwise.

    Raises:
      RuntimeError: since this is the fall through implementation.
    """
    # Note: not using NotImplementedError here since pylint then will complain
    # derived classes will need to implement the method, which should not
    # be the the case.
    raise RuntimeError('Missing implemention to analyze file object.')

  def GetFormatSpecification(self):
    """Retrieves the format specification.

       This is the fall through implementation that returns None.

    Returns:
      The format specification object (instance of analyzer.Specification)
      or None if the format cannot be defined by a specification object.
    """
    return
